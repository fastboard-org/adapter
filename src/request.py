import aiohttp

from fastapi.encoders import jsonable_encoder


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
                json=json_compatible_body,
            ) as response:
                json_body = await response.json()
                result = {
                    "body": json_body,
                    "status_code": response.status,
                    "headers": dict(response.headers),
                }
                return result
        except Exception:
            # Add a custom error message
            pass
