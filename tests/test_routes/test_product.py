from uuid import UUID

import pytest
from fastapi import status

from app.auth.jwt_handler import signJWT
from app.internal_models.models import Token
import json
from unittest.mock import patch

from unittest.mock import patch
import httpx
from unittest.mock import patch


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)  # Convert UUID to string for serialization
        return json.JSONEncoder.default(self, obj)


@pytest.mark.asyncio
async def test_get_products_no_auth(async_client):
    response = await async_client.get("/api/products")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid or Expired Token!'}


@pytest.mark.asyncio
async def test_get_products_no_product(async_client):

    token: Token = signJWT(email="test@test.com").get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/products", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_products(async_client, create_product):
    product_created_mock_response = {"id": "16be5a82-422a-88e2-7a75-9b7d9d41629f"}
    offer_data_mock_response = [{"id": "16be5a82-422a-88e2-7a75-9b7d9d41628f", "price":1500, "items_in_stock": 5, "product_id": "16be5a82-422a-88e2-7a75-9b7d9d41629f"},
                                {"id": "16be5a82-422a-88e2-7a75-9b7d9d41627f", "price":1600, "items_in_stock": 6, "product_id": "16be5a82-422a-88e2-7a75-9b7d9d41629f"}]
    with patch('app.external_service.offer_handler.httpx.AsyncClient.post') as mock_post:
        with patch('app.external_service.offer_handler.httpx.AsyncClient.get') as mock_get:
            mock_post.return_value = httpx.Response(status.HTTP_201_CREATED, json=product_created_mock_response)
            mock_get.return_value = httpx.Response(status.HTTP_200_OK, json=offer_data_mock_response)
            
            product = create_product()
            token: Token = signJWT(email="test@test.com").get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            response_create = await async_client.post(
                url="/api/product", data=json.dumps(product.dict(exclude={"id", "is_deleted"}), cls=CustomEncoder), headers=headers
            )

            response = await async_client.get("/api/products", headers=headers)

            assert response.status_code == status.HTTP_200_OK
            assert response.json()[0].get("id") == "16be5a82-422a-88e2-7a75-9b7d9d41628f"
            assert response.json()[0].get("price") == 1500
            assert response.json()[0].get("items_in_stock") == 5
            assert response.json()[1].get("id") == "16be5a82-422a-88e2-7a75-9b7d9d41627f"
            assert response.json()[1].get("price") == 1600
            assert response.json()[1].get("items_in_stock") == 6
            assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_product_by_id(async_client, create_product):
    product_created_mock_response = {"id": "16be5a82-422a-88e2-7a75-9b7d9d41629f"}
    offer_data_mock_response = [{"id": "16be5a82-422a-88e2-7a75-9b7d9d41628f", "price":1500, "items_in_stock": 5, "product_id": "16be5a82-422a-88e2-7a75-9b7d9d41629f"}]
    with patch('app.external_service.offer_handler.httpx.AsyncClient.post') as mock_post:
        with patch('app.external_service.offer_handler.httpx.AsyncClient.get') as mock_get:
            mock_post.return_value = httpx.Response(status.HTTP_201_CREATED, json=product_created_mock_response)
            mock_get.return_value = httpx.Response(status.HTTP_200_OK, json=offer_data_mock_response)
            product = create_product()
            token: Token = signJWT(email="test@test.com").get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            response_create = await async_client.post(
                        url="/api/product", data=json.dumps(product.dict(exclude={"id", "is_deleted"}), cls=CustomEncoder), headers=headers
                    )
            response = await async_client.get("/api/product/16be5a82-422a-88e2-7a75-9b7d9d41629f", headers=headers)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()[0].get("id") == "16be5a82-422a-88e2-7a75-9b7d9d41628f"
            assert response.json()[0].get("price") == 1500
            assert response.json()[0].get("items_in_stock") == 5
            assert len(response.json()) == 1
