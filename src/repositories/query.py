from request import make_request
from models.query import Query
from lib.parameters import replace_parameters
from errors import CustomException, ERR_UNSUPPORTED_QUERY_TYPE


class QueryRepository:
    url: str
    version: str

    def __init__(self, url: str, version: str):
        self.url = url
        self.version = version

    async def get_by_id(self, query_id: str):
        url = self.url + f"/v{self.version}/queries/{query_id}"
        query_response = await make_request(url=url, headers={}, method="GET")
        return query_response

    async def get_connection_by_id(self, connection_id: str):
        url = self.url + f"/v{self.version}/connections/{connection_id}"
        connection_response = await make_request(url=url, headers={}, method="GET")
        return connection_response

    async def execute_query(self, query: Query):
        if query.type == "REST":
            return await self.execute_api_query(query)
        if query.type == "MONGO":
            return None
        if query.type == "POSTGRES":
            return None
        raise CustomException(
            status_code=400,
            error_code=ERR_UNSUPPORTED_QUERY_TYPE,
            description=f"Unsupported query type: {query.type}",
        )

    async def execute_api_query(self, query: Query):
        parameters = {**query.variables, **query.parameters}
        # Fill header parameters
        headers = {}
        for key, value in query.headers.items():
            replaced_key = replace_parameters(key, parameters)
            replaced_value = replace_parameters(value, parameters)
            headers[replaced_key] = replaced_value

        # Fill body parameters
        body = {}
        for key, value in query.body.items():
            replaced_key = replace_parameters(key, parameters)
            replaced_value = replace_parameters(value, parameters)
            body[replaced_key] = replaced_value

        # Fill path parameters
        path = replace_parameters(query.path, parameters)

        url = query.credentials["main_url"] + path

        response = await make_request(
            url=url, headers=headers, method=query.method, body=body
        )
        return response
