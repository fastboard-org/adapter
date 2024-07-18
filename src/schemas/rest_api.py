from pydantic import BaseModel


class ExecuteQueryRequest(BaseModel):
    parameters: dict


class PreviewQueryRequest(BaseModel):
    parameters: dict
    method: str
    path: str
    headers: dict
    body: dict
