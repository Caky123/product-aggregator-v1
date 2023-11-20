from typing import Dict

from fastapi import APIRouter, Body, status

from app.auth.jwt_handler import signJWT
from app.internal_models.models import Token, User

router = APIRouter()


@router.post(
    "/token",
    tags=["token"],
    response_model=Token,
    summary="Get auth. token",
    description="Token expired after 10 minutes.",
    responses={
        status.HTTP_200_OK: {"description": "Token generated."},
    },
)
async def generate_token(user: User = Body(default=None)) -> Dict:
    return signJWT(user.email)
