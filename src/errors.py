from fastapi import (
    HTTPException,
)
from fastapi.responses import (
    JSONResponse,
)

ERR_INTERNAL = "A0"
ERR_BAD_REQUEST = "A1"
ERR_UNSUPPORTED_QUERY_TYPE = "A2"
ERR_QUERY_EXECUTION = "A3"
ERR_BAD_PARAMETERS = "A4"


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        description: str,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.description = description

    def __str__(self) -> str:
        return f"{self.description}"

    def create_json_response(
        self,
    ):
        print(f"Error: {self.error_code} - {self.description}")
        return JSONResponse(
            status_code=self.status_code,
            content={
                "error": {
                    "code": self.error_code,
                    "description": self.description,
                }
            },
        )


"""
Handler for exceptions raised due to validations errors in the request
"""


def handle_validation_error(_, exc) -> JSONResponse:
    error_messages = []
    for error in exc.errors():
        field_name = error["loc"]
        error_messages.append(f"{field_name}: {error['msg']}")
    message = ", ".join(error_messages)
    print(f"Validation error: {message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": ERR_BAD_REQUEST,
                "description": f"Request validation error - {message}",
            }
        },
    )


def handle_custom_exception(_, exc) -> JSONResponse:
    return exc.create_json_response()
