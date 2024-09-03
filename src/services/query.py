from repositories.query import QueryRepository
from errors import CustomException, ERR_UNSUPPORTED_QUERY_TYPE
from models.query import Query, ApiQuery, MongoQuery
from schemas.rest_api import ExecuteQueryRequest, PreviewQueryRequest


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
        if type == "REST":
            new_query = ApiQuery(
                type=type,
                credentials=connection["body"]["credentials"],
                variables=connection["body"]["variables"],
                method=query.method,
                parameters=query.parameters,
                path=query.path,
                headers=query.headers,
                body=query.body,
            )
        return await self.repository.execute_query(new_query)
