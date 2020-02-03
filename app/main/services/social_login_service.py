import logging
from ..services import user_service, facebook_service
from ..schemas import token

BLUESKY_PROVIDER = 'bluesky'
FACEBOOK_PROVIDER = 'facebook'

logger = logging.getLogger(__name__)


class ProviderUnsupportedError(Exception):
    pass


class SocialTokenError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class SocialLoginService():
    def __init__(self):
        pass

    async def get_user(self, db, social_token: token.SocialToken):
        user = None
        data = None

        if social_token.provider == FACEBOOK_PROVIDER:
            data = await facebook_service.get_user_data(social_token.token)
        else:
            raise ProviderUnsupportedError(
                f'Unsupported provider: {social_token.provider}')

        if data is None:
            raise SocialTokenError()

        user = user_service.get_user(db, email=data['email'])
        print(data)
        if user is None:
            raise UserNotFoundError('No user found for given credentials')

        return user