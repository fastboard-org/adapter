from fastapi import APIRouter, Depends
from repositories.query import QueryRepository
from configs.settings import settings
from services.query import QueryService
from schemas.rest_api import ExecuteQueryRequest, PreviewQueryRequest


AdapterRouter = APIRouter(prefix="/v1/adapter", tags=["adapter"])


def get_query_service():
    repository = QueryRepository(url=settings.dashboards_service_url, version="1")
    service = QueryService(repository)
    return service


@AdapterRouter.post("/{connection_id}/execute/{query_id}")
async def execute_query(
    connection_id: str,
    query_id: str,
    parameters: ExecuteQueryRequest,
    user_id: str,
    service: QueryService = Depends(get_query_service),
):
    return await service.execute_query(connection_id, query_id, parameters, user_id)


@AdapterRouter.post("/{connection_id}/preview")
async def preview_query(
    connection_id: str,
    query: PreviewQueryRequest,
    user_id: str,
    service: QueryService = Depends(get_query_service),
):
    return await service.preview_query(connection_id, query, user_id)
