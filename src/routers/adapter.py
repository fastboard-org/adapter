from fastapi import APIRouter, Depends
from repositories.query import QueryRepository
from configs.settings import settings
from services.query import QueryService
from schemas.query import ExecuteQueryRequest, PreviewQueryRequest


AdapterRouter = APIRouter(prefix="/v1/adapter", tags=["adapter"])


def get_query_service():
    repository = QueryRepository(url=settings.DASHBOARDS_SERVICE_URL, version="1")
    service = QueryService(repository)
    return service


@AdapterRouter.post("/embeddings/{query_id}")
async def create_embeddings(
    query_id: str,
    index_field: str,
    service: QueryService = Depends(get_query_service),
):
    return await service.create_embeddings(query_id, index_field)


@AdapterRouter.post("/execute/{query_id}")
async def execute_query(
    query_id: str,
    parameters: ExecuteQueryRequest,
    service: QueryService = Depends(get_query_service),
):
    return await service.execute_query(query_id, parameters)


@AdapterRouter.post("/{connection_id}/preview")
async def preview_query(
    connection_id: str,
    query: PreviewQueryRequest,
    service: QueryService = Depends(get_query_service),
):
    return await service.preview_query(connection_id, query)
