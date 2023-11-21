from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from typing import List
from app.auth.jwt_bearer import jwtBearer
from app.db.err import EntityDoesNotExist
from app.db.product_database import ProductDatabase
from app.db.sessions import get_database
from app.internal_models.models import (CreateProductRequest,
                                        CreateProductResponse,
                                        DeleteProductResponse, ProductResponse,
                                        ProductOfferResponse,
                                        UpdateProductRequest,
                                        UpdateProductResponse)

router = APIRouter()


@router.post(
    "/product",
    tags=["products"],
    dependencies=[Depends(jwtBearer())],
    summary="Create product.",
    description="Create product.",
    responses={
        status.HTTP_201_CREATED: {"description": "Product was successfully created."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "External offer service authorize fail."
        },
    },
    response_model=CreateProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_products(
    create_request: CreateProductRequest = Body(),
    database: ProductDatabase = Depends(get_database(ProductDatabase)),
) -> CreateProductResponse:
    return await database.create(product_create=create_request)


@router.put(
    "/product/{product_id}",
    tags=["products"],
    dependencies=[Depends(jwtBearer())],
    summary="Update product.",
    description="Update product.",
    responses={
        status.HTTP_200_OK: {"description": "Product was successfully updated."},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found."},
    },
    response_model=UpdateProductResponse,
)
async def update_product(
    product_id: UUID,
    update_request: UpdateProductRequest = Body(),
    database: ProductDatabase = Depends(get_database(ProductDatabase)),
) -> UpdateProductResponse:
    try:
        return await database.update(
            product_id=product_id, product_update=update_request
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )


@router.delete(
    "/product/{product_id}",
    tags=["products"],
    dependencies=[Depends(jwtBearer())],
    summary="Remove product.",
    description="Remove product.",
    responses={
        status.HTTP_200_OK: {"description": "Product was removed."},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found."},
    },
    response_model=DeleteProductResponse,
)
async def delete_product(
    product_id: UUID, database: ProductDatabase = Depends(get_database(ProductDatabase))
) -> DeleteProductResponse:
    try:
        return await database.delete(product_id=product_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )


@router.get(
    "/product/{product_id}",
    tags=["products"],
    dependencies=[Depends(jwtBearer())],
    summary="Get product.",
    description="Get product.",
    responses={
        status.HTTP_200_OK: {"description": "Product was retrieved."},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found."},
    },
    response_model=ProductResponse,
)
async def get_product(
    product_id: UUID, database: ProductDatabase = Depends(get_database(ProductDatabase))
) -> ProductResponse:
    try:
        return await database.get(product_id=product_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )


@router.get(
    "/products",
    tags=["products"],
    dependencies=[Depends(jwtBearer())],
    summary="Get all products info.",
    description="Get all undeleted products.",
    responses={
        status.HTTP_200_OK: {"description": "Products was retrieved."},
        status.HTTP_404_NOT_FOUND: {"description": "Products not found."},
    },
    response_model=List[ProductOfferResponse],
)
async def get_products(
    database: ProductDatabase = Depends(get_database(ProductDatabase)),
) -> List[ProductResponse]:
    try:
        return await database.get_all()
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Products not found."
        )
