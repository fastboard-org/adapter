from fastapi import FastAPI
import uvicorn
from configs.settings import settings
from routers.adapter import AdapterRouter
from fastapi.exceptions import RequestValidationError
from errors import CustomException, handle_validation_error, handle_custom_exception


app = FastAPI()
app.include_router(AdapterRouter)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(CustomException, handle_custom_exception)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
