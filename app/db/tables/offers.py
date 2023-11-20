from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.db.tables.base import TimestampModel, UUIDModel
from app.db.tables.products import Product


class OfferBase(SQLModel):
    price: int = Field(nullable=False)
    items_in_stock: int = Field(nullable=False)


class Offer(OfferBase, UUIDModel, TimestampModel, table=True):
    __tablename__ = "offers"
    product_id: UUID = Field(default=None, foreign_key="products.id")
    offer_id: UUID = Field(default=None)
    product: Optional[Product] = Relationship(back_populates="offers")
