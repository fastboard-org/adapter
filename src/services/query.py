from repositories.query import QueryRepository
from errors import CustomException, ERR_UNSUPPORTED_QUERY_TYPE, ERR_BAD_PARAMETERS
from models.query import ApiQuery, MongoQuery, VectorSearchQuery
from schemas.query import ExecuteQueryRequest, PreviewQueryRequest
from lib.encryption import decrypt
from openai import OpenAI
import tiktoken


class QueryService:
    def __init__(self, repository: QueryRepository):
        self.repository = repository

    async def execute_query(
        self,
        query_id: str,
        parameters: ExecuteQueryRequest,
    ):
        query = await self.repository.get_by_id(query_id)
        if query["status_code"] != 200:
            error = query["body"]["error"]
            raise CustomException(
                status_code=query["status_code"],
                error_code=error["code"],
                description=error["description"],
            )

        type = query["body"]["connection"]["type"]
        credentials = query["body"]["connection"]["credentials"]
        variables = query["body"]["connection"]["variables"]

        if type == "REST":
            body = (
                query["body"]["metadata"]["body"]
                if "body" in query["body"]["metadata"]
                else {}
            )
            headers = (
                query["body"]["metadata"]["headers"]
                if "headers" in query["body"]["metadata"]
                else {}
            )
            new_query = ApiQuery(
                type=type,
                credentials=credentials,
                variables=variables,
                method=query["body"]["metadata"]["method"],
                parameters=parameters.parameters,
                path=query["body"]["metadata"]["path"],
                headers=headers,
                body=body,
            )
        elif type == "MONGO":
            method = query["body"]["metadata"]["method"]
            if method == "vectorSearch":
                credentials["openai_api_key"] = decrypt(credentials["openai_api_key"])
                new_query = VectorSearchQuery(
                    type="VECTOR_SEARCH",
                    credentials=credentials,
                    variables=variables,
                    parameters=parameters.parameters,
                    method=query["body"]["metadata"]["method"],
                    collection=query["body"]["metadata"]["collection"],
                    index_created=query["body"]["metadata"]["index_created"],
                    embeddings_created=query["body"]["metadata"]["embeddings_created"],
                    query=query["body"]["metadata"]["query"],
                    limit=query["body"]["metadata"]["limit"],
                    num_candidates=query["body"]["metadata"]["num_candidates"],
                )
            else:
                new_query = MongoQuery(
                    type=type,
                    credentials=credentials,
                    variables=variables,
                    parameters=parameters.parameters,
                    method=query["body"]["metadata"]["method"],
                    collection=query["body"]["metadata"]["collection"],
                    filter_body=query["body"]["metadata"]["filter_body"],
                    update_body=query["body"]["metadata"]["update_body"],
                )
        else:
            raise CustomException(
                status_code=400,
                error_code=ERR_UNSUPPORTED_QUERY_TYPE,
                description=f"Unsupported query type: {type}",
            )
        res = await self.repository.execute_query(new_query)
        print(f"res: {res}")
        return res

    async def preview_query(self, connection_id: str, query: PreviewQueryRequest):
        connection = await self.repository.get_connection_by_id(connection_id)
        if connection["status_code"] != 200:
            error = connection["body"]["error"]
            raise CustomException(
                status_code=connection["status_code"],
                error_code=error["code"],
                description=error["description"],
            )

        type = connection["body"]["type"]
        credentials = connection["body"]["credentials"]
        variables = connection["body"]["variables"]

        if type == "REST":
            try:
                new_query = ApiQuery(
                    type=type,
                    credentials=credentials,
                    variables=variables,
                    method=query.connection_metadata.method,
                    parameters=query.parameters,
                    path=query.connection_metadata.path,
                    headers=query.connection_metadata.headers,
                    body=query.connection_metadata.body,
                )
            except Exception as e:
                raise CustomException(
                    status_code=400,
                    error_code=ERR_BAD_PARAMETERS,
                    description=f"Error creating API query from parameters: {e}",
                )

        elif type == "MONGO":
            method = query.connection_metadata.method
            if method == "vectorSearch":
                try:
                    credentials["openai_api_key"] = decrypt(credentials["openai_api_key"])
                    new_query = VectorSearchQuery(
                        type="VECTOR_SEARCH",
                        credentials=credentials,
                        variables=variables,
                        parameters=query.parameters,
                        method=query.connection_metadata.method,
                        collection=query.connection_metadata.collection,
                        index_created=query.connection_metadata.index_created,
                        embeddings_created=query.connection_metadata.embeddings_created,
                        query=query.connection_metadata.query,
                        limit=query.connection_metadata.limit,
                        num_candidates=query.connection_metadata.num_candidates,
                    )
                except Exception as e:
                    raise CustomException(
                        status_code=400,
                        error_code=ERR_BAD_PARAMETERS,
                        description=f"Error creating vector search query: {e}",
                    )
            else:
                try:
                    new_query = MongoQuery(
                        type=type,
                        credentials=credentials,
                        variables=variables,
                        parameters=query.parameters,
                        method=query.connection_metadata.method,
                        collection=query.connection_metadata.collection,
                        filter_body=query.connection_metadata.filter_body,
                        update_body=query.connection_metadata.update_body,
                    )
                except Exception as e:
                    raise CustomException(
                        status_code=400,
                        error_code=ERR_BAD_PARAMETERS,
                        description=f"Error creating Mongo query from parameters: {e}",
                    )
        else:
            raise CustomException(
                status_code=400,
                error_code=ERR_UNSUPPORTED_QUERY_TYPE,
                description=f"Unsupported query type: {type}",
            )

        return await self.repository.execute_query(new_query)

    async def create_embeddings(self, query_id: str, index_field: str):
        query = await self.repository.get_by_id(query_id)
        if query["status_code"] != 200:
            error = query["body"]["error"]
            raise CustomException(
                status_code=query["status_code"],
                error_code=error["code"],
                description=error["description"],
            )

        type = query["body"]["connection"]["type"]
        credentials = query["body"]["connection"]["credentials"]

        if type == "MONGO":
            method = query["body"]["metadata"]["method"]
            if method == "vectorSearch":
                credentials["openai_api_key"] = decrypt(credentials["openai_api_key"])
                model = "text-embedding-ada-002"
                openai_client = OpenAI(api_key=credentials["openai_api_key"])

                # get all the documents in the collection
                documents = await self.repository.get_all_documents_field(
                    connection_string=credentials["main_url"],
                    collection=query["body"]["metadata"]["collection"],
                    field=index_field,
                )

                # for each document, get the embeddings for the index_field
                update_dict = {}
                # we filter out the documents that don't have the index_field or are empty
                documents["body"] = [
                    document
                    for document in documents["body"]
                    if index_field in document and document[index_field]
                ]
                query_texts = [
                    document[index_field].strip() for document in documents["body"]
                ]
                enc = tiktoken.encoding_for_model(model)
                tokens = [len(enc.encode(text)) for text in query_texts]
                total_tokens = sum(tokens)
                print(f"Total tokens: {total_tokens}")
                # The input parameter may not take a list longer than 2048 elements
                # (chunks of text).
                # The total number of tokens across all list elements of the input
                # parameter cannot exceed 1,000,000. (Because the rate limit is
                # 1,000,000 tokens per minute.)
                # Each individual array element (chunk of text) cannot be more
                # than 8191 tokens.
                if total_tokens > 1000000:
                    print("Total tokens > 1M")
                    batch_size = 2048
                    n_batches = len(query_texts) // batch_size + 1
                    embeddings = []
                    print(f"n_batches: {n_batches}")
                    for i in range(n_batches):
                        print(f"Batch {i}")
                        batch = query_texts[i * batch_size: (i + 1) * batch_size]
                        embeddings_response = openai_client.embeddings.create(
                            input=batch, model=model
                        )
                        embeddings_usage = embeddings_response.usage
                        print(embeddings_usage)
                        print(embeddings_usage)
                        embeddings += embeddings_response.data
                    for i, document in enumerate(documents["body"]):
                        id = document["_id"]
                        update_dict[id] = embeddings[i].embedding
                else:
                    print("Total tokens <= 1M")
                    embeddings_response = openai_client.embeddings.create(
                        input=query_texts, model=model
                    )
                    embeddings_usage = embeddings_response.usage
                    print(embeddings_usage)
                    embeddings = embeddings_response.data
                    for i, document in enumerate(documents["body"]):
                        id = document["_id"]
                        update_dict[id] = embeddings[i].embedding

                # update the document with the new field "embedding"
                response = await self.repository.patch_all_documents_field(
                    connection_string=credentials["main_url"],
                    collection=query["body"]["metadata"]["collection"],
                    values=update_dict,
                )

                metadata = query["body"]["metadata"]
                metadata["embeddings_created"] = True
                metadata["index_field"] = index_field
                response = await self.repository.update_query(
                    query_id, {"metadata": metadata, "user_id": query["body"]["user_id"]}
                )

                return response

            else:
                raise CustomException(
                    status_code=400,
                    error_code=ERR_UNSUPPORTED_QUERY_TYPE,
                    description=f"Unsupported query method: {method}",
                )
        else:
            raise CustomException(
                status_code=400,
                error_code=ERR_UNSUPPORTED_QUERY_TYPE,
                description=f"Unsupported query type: {type}",
            )
