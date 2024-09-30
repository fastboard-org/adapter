from pydantic import BaseModel
from typing import Union


class ExecuteQueryRequest(BaseModel):
    parameters: dict


class ApiMetadata(BaseModel):
    method: str
    path: str
    headers: dict
    body: dict


class MongoMetadata(BaseModel):
    method: str
    collection: str
    filter_body: Union[dict, list, str]
    update_body: Union[dict, list, str]


class MongoVectorSearchMetadata(BaseModel):
    method: str
    collection: str
    index_created: bool
    embeddings_created: bool
    query: str
    limit: int
    num_candidates: int


class PreviewQueryRequest(BaseModel):
    parameters: dict
    connection_metadata: Union[ApiMetadata, MongoMetadata, MongoVectorSearchMetadata]
