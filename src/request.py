import aiohttp

from fastapi.encoders import jsonable_encoder
from errors import CustomException, ERR_INTERNAL


async def make_request(url, headers, method, body={}, params={}):
    json_compatible_body = jsonable_encoder(body)
    url = (
        url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
        if len(params) > 0
        else url
    )
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method,
                url,
                headers=headers,
                json=json_compatible_body,
            ) as response:
                if response.content_type == "application/json":
                    json_body = await response.json()
                else:
                    json_body = await response.text()
                result = {
                    "body": json_body,
                    "status_code": response.status,
                    "headers": dict(response.headers),
                }
                return result
        except Exception as e:
            raise CustomException(
                500,
                ERR_INTERNAL,
                f"An error ocurred while trying to make the request: {str(e)}",
            )
