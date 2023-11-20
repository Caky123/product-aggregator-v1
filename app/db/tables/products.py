from typing import List

from sqlmodel import Field, Relationship, SQLModel

from app.db.tables.base import UUIDModel


class ProductBase(SQLModel):
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)


class Product(ProductBase, UUIDModel, table=True):
    __tablename__ = "products"
    is_deleted: bool = Field(default=False)
    offers: List["Offer"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}, back_populates="product"
    )
