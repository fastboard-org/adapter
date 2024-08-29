from fastapi import APIRouter, Depends
from repositories.query import QueryRepository
from configs.settings import settings
from services.query import QueryService
from schemas.rest_api import ExecuteQueryRequest, PreviewQueryRequest


AdapterRouter = APIRouter(prefix="/v1/adapter", tags=["adapter"])


def get_query_service():
    repository = QueryRepository(url=settings.DASHBOARDS_SERVICE_URL, version="1")
    service = QueryService(repository)
    return service


@AdapterRouter.post("/{connection_id}/execute/{query_id}")
async def execute_query(
    connection_id: str,
    query_id: str,
    parameters: ExecuteQueryRequest,
    service: QueryService = Depends(get_query_service),
):
    return await service.execute_query(connection_id, query_id, parameters)


@AdapterRouter.post("/{connection_id}/preview")
async def preview_query(
    connection_id: str,
    query: PreviewQueryRequest,
    service: QueryService = Depends(get_query_service),
):
    return await service.preview_query(connection_id, query)
