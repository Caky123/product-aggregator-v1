from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Extra
from sqlmodel import Field


class BaseInterfaceModel(BaseModel):
    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True


class ProductRequest(BaseInterfaceModel):
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)


class ProductResponse(ProductRequest):
    id: UUID


class CreateProductRequest(ProductRequest):
    ...


class CreateProductResponse(ProductResponse):
    ...


class UpdateProductRequest(ProductRequest):
    ...


class DeleteProductResponse(ProductResponse):
    ...


class UpdateProductResponse(CreateProductRequest):
    ...


class OfferB(BaseInterfaceModel):
    created_at: datetime
    price: int
    items_in_stock: int


class OfferBase(OfferB):
    offer_id: UUID


class OfferResponse(OfferBase):
    ...


class ProductOfferResponse(ProductResponse):
    offers: List[OfferBase]


class Paging(BaseInterfaceModel):
    page: int
    limit: int
    offset: int
    total_pages: int


class OfferHistoryResponse(BaseInterfaceModel):
    id: UUID
    history: List[OfferB]


class OfferHistoryPagingResponse(OfferHistoryResponse):
    paging: Paging


class OfferTrendResponse(OfferHistoryResponse):
    price_trend: float


class Token(BaseInterfaceModel):
    access_token: str
    token_type: str


class User(BaseInterfaceModel):
    email: EmailStr = Field(default=None)
