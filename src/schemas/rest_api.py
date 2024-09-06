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
    filter_body: dict
    update_body: dict


class PreviewQueryRequest(BaseModel):
    parameters: dict
    connection_metadata: Union[ApiMetadata, MongoMetadata]
