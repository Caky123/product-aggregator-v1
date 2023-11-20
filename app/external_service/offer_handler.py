import json
from typing import Dict
from uuid import UUID

from fastapi import FastAPI, HTTPException, status

import httpx
from app.settings.conf import settings

app = FastAPI()

API_URL = settings.offer_ms_api_url


async def authorize() -> Dict:
    headers = {"Bearer": settings.refresh_token}
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL + "auth", headers=headers)
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Lost external token for offer service..wait a moment and try again",
            )
        settings.access_token = response.json().get("access_token")
        return response.status_code


async def register_product(id: UUID, name: str, description: str) -> int:
    try_count = 3
    async with httpx.AsyncClient() as client:
        payload = json.dumps({"id": str(id), "name": name, "description": description})

        while try_count > 0:
            headers = {"Bearer": settings.access_token}
            response = await client.post(
                API_URL + "products/register", content=payload, headers=headers
            )
            if response.status_code == status.HTTP_201_CREATED:
                break
            else:
                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    await authorize()
                try_count -= 1

        return response.status_code


async def get_product_offers(id: UUID) -> Dict:
    try_count = 3
    async with httpx.AsyncClient() as client:
        while try_count > 0:
            headers = {"Bearer": settings.access_token}

            response = await client.get(
                API_URL + f"products/{id}/offers", headers=headers
            )

            if response.status_code == status.HTTP_200_OK:
                break
            else:
                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    await authorize()
                try_count -= 1

        return {"status_code": response.status_code, "data": response.json()}
