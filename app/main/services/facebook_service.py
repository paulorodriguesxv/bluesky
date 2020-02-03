import aiohttp
from http import HTTPStatus
from aiohttp.resolver import AsyncResolver
from aiohttp import web


async def get_user_data(token):
    base_url = 'https://graph.facebook.com'
    url = f"{base_url}/me?access_token={token}&fields=id,email"

    data = {}
    status = HTTPStatus.SERVICE_UNAVAILABLE

    async with aiohttp.ClientSession(connector=None) as session:
        async with session.get(url) as response:
            data = await response.json()
            status = response.status
            if status >= HTTPStatus.BAD_REQUEST:
                raise SocialTokenError(data)

    return data
