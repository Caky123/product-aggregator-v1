from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_handler import decodeJWT


class jwtBearer(HTTPBearer):
    def __init__(self, auto_Error: bool = False):
        super(jwtBearer, self).__init__(auto_error=auto_Error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(
            jwtBearer, self
        ).__call__(request)

        if self.is_accessed_allowed(credentials):
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or Expired Token!",
            )

    def is_accessed_allowed(self, credentials: HTTPAuthorizationCredentials) -> bool:
        if credentials:
            payload = decodeJWT(credentials.credentials)

            if payload and credentials.scheme == "Bearer":
                return True
        return False
