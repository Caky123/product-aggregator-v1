# Signing, decoding, encoding and returning JWT

import time

from jose import jwt

from app.db.err import EntityDoesNotExist
from app.internal_models.models import Token
from app.settings.conf import settings

JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = settings.jwt_algorithm


# Returns the generated token (JWT)
def token_response(token: str) -> Token:
    return {
        "access_token": token,
        "token_type": "Bearer",
    }


def signJWT(email: str) -> Token:
    payload = {"email": email, "expire": time.time() + settings.jwt_expire}

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token if decode_token["expire"] >= time.time() else None
    except EntityDoesNotExist:
        raise EntityDoesNotExist
