from connections.api_request import make_request
from connections.mongo_connection import execute_query, execute_vector_search, bulk_update
from models.query import Query, ApiQuery, MongoQuery, VectorSearchQuery
from lib.parameters import replace_parameters
from errors import (
    CustomException,
    ERR_UNSUPPORTED_QUERY_TYPE,
    ERR_BAD_PARAMETERS,
    ERR_INTERNAL,
)
import re
from configs.settings import settings
from lib.object_id import replace_objectid_strings


class QueryRepository:
    url: str
    version: str

    def __init__(self, url: str, version: str):
        self.url = url
        self.version = version

    async def get_by_id(self, query_id: str):
        url = self.url + f"/v{self.version}/queries/{query_id}"
        query_response = await make_request(
            url=url, headers={"api_key": settings.API_KEY}, method="GET"
        )
        return query_response

    async def get_connection_by_id(self, connection_id: str):
        url = self.url + f"/v{self.version}/connections/{connection_id}"
        connection_response = await make_request(
            url=url, headers={"api_key": settings.API_KEY}, method="GET"
        )
        return connection_response

    async def update_query(self, query_id: str, data: dict):
        url = self.url + f"/v{self.version}/queries/{query_id}"
        query_response = await make_request(
            url=url, headers={"api_key": settings.API_KEY}, method="PATCH", body=data
        )
        return query_response

    async def execute_query(self, query: Query):
        if query.type == "REST":
            return await self.execute_api_query(query)
        if query.type == "MONGO":
            return await self.execute_mongo_query(query)
        if query.type == "VECTOR_SEARCH":
            return await self.execute_vector_search_query(query)
        if query.type == "POSTGRES":
            return None
        raise CustomException(
            status_code=400,
            error_code=ERR_UNSUPPORTED_QUERY_TYPE,
            description=f"Unsupported query type: {query.type}",
        )

    async def execute_api_query(self, query: ApiQuery):
        parameters = {**query.variables, **query.parameters}
        used_parameters = set()

        # Fill header parameters
        headers = {}
        for key, value in query.headers.items():
            replaced_key = replace_parameters(key, parameters, used_parameters)
            replaced_value = replace_parameters(value, parameters, used_parameters)
            headers[replaced_key] = replaced_value

        # Fill body parameters
        body = {}
        for key, value in query.body.items():
            replaced_key = replace_parameters(key, parameters, used_parameters)
            replaced_value = replace_parameters(value, parameters, used_parameters)
            body[replaced_key] = replaced_value

        # Fill path parameters
        path = replace_parameters(query.path, parameters, used_parameters)

        url = query.credentials["main_url"] + path

        # Validate that all parameters were used
        unused_parameters = set(parameters.keys()) - used_parameters
        if "token" in unused_parameters:
            unused_parameters.remove("token")
        if unused_parameters:
            raise CustomException(
                status_code=400,
                error_code=ERR_BAD_PARAMETERS,
                description=f"Unused parameters in input: {unused_parameters}",
            )

        # Validate that all placeholders were replaced
        all_placeholders = re.findall(r"\{\{(.*?)\}\}", path)
        all_placeholders += [
            match
            for k, v in headers.items()
            for match in re.findall(r"\{\{(.*?)\}\}", k + v)
        ]
        all_placeholders += [
            match
            for k, v in body.items()
            for match in re.findall(r"\{\{(.*?)\}\}", k + str(v))
        ]

        missing_parameters = set(all_placeholders) - set(parameters.keys())
        if "token" in missing_parameters:
            missing_parameters.remove("token")
        if missing_parameters:
            raise CustomException(
                status_code=400,
                error_code=ERR_BAD_PARAMETERS,
                description=f"Missing parameters in input: {missing_parameters}",
            )

        response = await make_request(
            url=url, headers=headers, method=query.method, body=body
        )
        return response

    async def execute_mongo_query(self, query: MongoQuery):
        parameters = {**query.variables, **query.parameters}
        used_parameters = set()

        # Fill filter parameters
        filter_body = replace_parameters(query.filter_body, parameters, used_parameters)

        # Fill update parameters
        update_body = replace_parameters(query.update_body, parameters, used_parameters)

        # Validate that all parameters were used
        unused_parameters = set(parameters.keys()) - used_parameters
        if "token" in unused_parameters:
            unused_parameters.remove("token")
        if unused_parameters:
            raise CustomException(
                status_code=400,
                error_code=ERR_BAD_PARAMETERS,
                description=f"Unused parameters in input: {unused_parameters}",
            )

        # Validate that all placeholders were replaced
        all_placeholders = re.findall(
            r"\{\{(.*?)\}\}", str(filter_body) + str(update_body)
        )
        missing_parameters = set(all_placeholders) - set(parameters.keys())
        if "token" in missing_parameters:
            missing_parameters.remove("token")
        if missing_parameters:
            raise CustomException(
                status_code=400,
                error_code=ERR_BAD_PARAMETERS,
                description=f"Missing parameters in input: {missing_parameters}",
            )

        try:
            response = await execute_query(
                connection_string=query.credentials["main_url"],
                collection=query.collection,
                method=query.method,
                filter_body=replace_objectid_strings(filter_body),
                update_body=replace_objectid_strings(update_body),
            )

            return response
        except Exception as e:
            raise CustomException(
                status_code=500,
                error_code=ERR_INTERNAL,
                description=f"Error while executing query: {str(e)}",
            )

    async def execute_vector_search_query(self, query: VectorSearchQuery):
        parameters = {**query.variables, **query.parameters}
        used_parameters = set()

        # Fill query parameters
        query_text = replace_parameters(query.query, parameters, used_parameters)

        # Validate that all parameters were used
        unused_parameters = set(parameters.keys()) - used_parameters
        if "token" in unused_parameters:
            unused_parameters.remove("token")
        if unused_parameters:
            raise CustomException(
                status_code=400,
                error_code=ERR_BAD_PARAMETERS,
                description=f"Unused parameters in input: {unused_parameters}",
            )

        # Validate that all placeholders were replaced
        all_placeholders = re.findall(r"\{\{(.*?)\}\}", query_text)
        missing_parameters = set(all_placeholders) - set(parameters.keys())
        if "token" in missing_parameters:
            missing_parameters.remove("token")
        if missing_parameters:
            raise CustomException(
                status_code=400,
                error_code=ERR_BAD_PARAMETERS,
                description=f"Missing parameters in input: {missing_parameters}",
            )

        try:
            response = await execute_vector_search(
                connection_string=query.credentials["main_url"],
                api_key=query.credentials["openai_api_key"],
                collection=query.collection,
                query=query_text,
                limit=query.limit,
                num_candidates=query.num_candidates,
            )

            return response
        except Exception as e:
            raise CustomException(
                status_code=500,
                error_code=ERR_INTERNAL,
                description=f"Error while executing query: {str(e)}",
            )

    async def get_all_documents_field(
        self, connection_string: str, collection: str, field: str
    ):
        try:
            # we filter the documents to only get the field
            response = await execute_query(
                connection_string=connection_string,
                collection=collection,
                method="aggregate",
                # filter body to only obtain _id and the field
                filter_body=[{"$project": {"_id": 1, field: 1}}],
                update_body={},
            )
            return response
        except Exception as e:
            raise CustomException(
                status_code=500,
                error_code=ERR_INTERNAL,
                description=f"Error while executing query: {str(e)}",
            )

    async def patch_all_documents_field(
        self, connection_string: str, collection: str, values: dict
    ):
        # values is a dictionary with the _id as key and the field value as value
        try:
            response = await bulk_update(
                connection_string=connection_string,
                collection=collection,
                updates=values,
            )
            return response
        except Exception as e:
            raise CustomException(
                status_code=500,
                error_code=ERR_INTERNAL,
                description=f"Error while executing query: {str(e)}",
            )
