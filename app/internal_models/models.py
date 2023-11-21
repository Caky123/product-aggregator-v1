from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Extra, Field


class BaseInterfaceModel(BaseModel):
    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True


class ProductRequest(BaseInterfaceModel):
    name: str = Field(example="product-name")
    description: str = Field(example="product-description")


class ProductResponse(ProductRequest):
    id: UUID = Field(example=UUID("a38269b5-1d44-434f-94f4-6c3ffb2a2ee6"))


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
    created_at: datetime = Field(example="2011-08-12T20:17:46.384")
    price: int = Field(example=100)
    items_in_stock: int = Field(example=30)


class OfferBase(OfferB):
    offer_id: str = Field(example="a38269b5-1d44-434f-94f4-6c3ffb2a2ee6")


class OfferResponse(OfferBase):
    ...


class ProductOfferResponse(ProductResponse):
    offers: List[OfferBase]


class Paging(BaseInterfaceModel):
    page: int = Field(example=10)
    limit: int = Field(example=100)
    offset: int = Field(example=10)
    total_pages: int = Field(example=10)


class OfferHistoryResponse(BaseInterfaceModel):
    id: str = Field(example="a38269b5-1d44-434f-94f4-6c3ffb2a2ee6")
    history: List[OfferB]


class OfferHistoryPagingResponse(OfferHistoryResponse):
    paging: Paging


class OfferTrendResponse(OfferHistoryResponse):
    price_trend: float = Field(example=12.5)


class Token(BaseInterfaceModel):
    access_token: str
    token_type: str


class User(BaseInterfaceModel):
    email: EmailStr = Field(default=None)
