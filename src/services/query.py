from repositories.query import QueryRepository
from errors import CustomException
from models.query import Query
from schemas.rest_api import ExecuteQueryRequest, PreviewQueryRequest


class QueryService:
    def __init__(self, repository: QueryRepository):
        self.repository = repository

    async def execute_query(
        self, connection_id: str, query_id: str, parameters: ExecuteQueryRequest
    ):
        query = await self.repository.get_by_id(query_id)
        if query["status_code"] != 200:
            error = query["body"]["error"]
            raise CustomException(
                status_code=query["status_code"],
                error_code=error["code"],
                description=error["description"],
            )
        connection = await self.repository.get_connection_by_id(
            connection_id=connection_id
        )
        if connection["status_code"] != 200:
            error = connection["body"]["error"]
            raise CustomException(
                status_code=connection["status_code"],
                error_code=error["code"],
                description=error["description"],
            )
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
        new_query = Query(
            type=connection["body"]["type"],
            credentials=connection["body"]["credentials"],
            variables=connection["body"]["variables"],
            method=query["body"]["metadata"]["method"],
            parameters=parameters.parameters,
            path=query["body"]["metadata"]["path"],
            headers=headers,
            body=body,
        )
        response = await self.repository.execute_query(new_query)
        return response

    async def preview_query(self, connection_id: str, query: PreviewQueryRequest):
        connection = await self.repository.get_connection_by_id(connection_id)
        if connection["status_code"] != 200:
            error = connection["body"]["error"]
            raise CustomException(
                status_code=connection["status_code"],
                error_code=error["code"],
                description=error["description"],
            )
        new_query = Query(
            type=connection["body"]["type"],
            credentials=connection["body"]["credentials"],
            variables=connection["body"]["variables"],
            method=query.method,
            parameters=query.parameters,
            path=query.path,
            headers=query.headers,
            body=query.body,
        )
        response = await self.repository.execute_query(new_query)
        return response
