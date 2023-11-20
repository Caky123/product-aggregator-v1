from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import status
from sqlalchemy import and_, func, select
from sqlalchemy.sql.expression import false
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.err import (EntityDoesNotCreatedByOffers,
                        EntityDoesNotCreatedByRegistration, EntityDoesNotExist,
                        StartTimeAfterEndTime)
from app.db.tables.offers import Offer
from app.db.tables.products import Product
from app.external_service.offer_handler import (get_product_offers,
                                                register_product)
from app.internal_models.models import (CreateProductRequest,
                                        CreateProductResponse,
                                        DeleteProductResponse, OfferB,
                                        OfferHistoryPagingResponse,
                                        OfferResponse, ProductOfferResponse,
                                        UpdateProductRequest, UpdateProductResponse)
from app.paging.paging import Pagination


class ProductDatabase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_instance(self, product_id: UUID):
        statement = select(Product).filter(
            and_(Product.id == product_id, Product.is_deleted == false())
        )
        results = await self.session.exec(statement)
        response = results.scalars().first()
        return response

    async def _get_instances(self):
        statement = select(Product).filter(Product.is_deleted == false())
        results = await self.session.exec(statement)
        response = results.scalars().all()
        return response

    async def _get_offer_instances(self, product_id):
        subquery = (
            select(Offer.offer_id, func.max(Offer.created_at).label("max_created_at"))
            .join(Product)
            .filter(and_(Product.id == product_id, Product.is_deleted == false()))
            .group_by(Offer.offer_id)
            .subquery()
        )

        stmt = select(Offer).join(
            subquery,
            and_(
                Offer.offer_id == subquery.c.offer_id,
                Offer.created_at == subquery.c.max_created_at,
            ),
        )

        results = await self.session.exec(stmt)
        response = results.fetchall()
        return response

    async def create(
        self, product_create: CreateProductRequest
    ) -> CreateProductResponse:
        product = Product.from_orm(product_create)

        # Register product
        response_register_product = await register_product(
            id=product.id, name=product.name, description=product.description
        )

        if response_register_product != status.HTTP_201_CREATED:
            raise EntityDoesNotCreatedByRegistration

        # Get product offers
        response_product_offers = await get_product_offers(id=product.id)

        if response_product_offers.get("status_code") != status.HTTP_200_OK:
            raise EntityDoesNotCreatedByOffers
        else:
            for offer_data in response_product_offers.get("data", []):
                offer = Offer(
                    offer_id=offer_data.get("id", 0),
                    price=offer_data.get("price", 0),
                    items_in_stock=offer_data.get("items_in_stock", 0),
                )
                product.offers.append(offer)

        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)
        return CreateProductResponse(**product.dict(exclude={"is_deleted"}))

    async def update(
        self, product_id: UUID, product_update=UpdateProductRequest
    ) -> UpdateProductResponse:
        product = await self._get_instance(product_id)
        if not product:
            raise EntityDoesNotExist

        product_data = product_update.dict(exclude_unset=True, exclude={"id"})
        for key, value in product_data.items():
            setattr(product, key, value)

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)

        return UpdateProductResponse(**product.dict(exclude={"id", "is_deleted"}))

    async def delete(self, product_id: UUID) -> DeleteProductResponse:
        product = await self._get_instance(product_id)
        if not product:
            raise EntityDoesNotExist
        # Soft delete
        product.is_deleted = True
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return DeleteProductResponse(**product.dict(exclude={"is_deleted"}))

    async def get(self, product_id: UUID) -> Optional[ProductOfferResponse]:
        product = await self._get_instance(product_id)

        if not product:
            raise EntityDoesNotExist

        offers_db = await self._get_offer_instances(product_id)

        if not offers_db:
            raise EntityDoesNotExist

        offers = []

        for o in offers_db:
            offers.append(OfferResponse(**o[0].dict(exclude={"id", "product_id"})))

        return ProductOfferResponse(
            **product.dict(exclude={"is_deleted"}), offers=offers
        )

    async def get_all(self) -> Optional[List[ProductOfferResponse]]:
        products = await self._get_instances()

        if not products:
            raise EntityDoesNotExist

        response = []
        for product in products:
            offers_db = await self._get_offer_instances(product.id)

            offers = []
            for o in offers_db:
                offers.append(
                    OfferResponse(**o[0].dict(exclude={"id", "product_id"}))
                )

            response.append(
                ProductOfferResponse(
                    **product.dict(exclude={"is_deleted"}), offers=offers
                )
            )
        return response

    # Offers
    async def _get_offer_history(
        self,
        offer_id: UUID,
        start_time: datetime = datetime.min,
        end_time: datetime = datetime.max,
        limit: int = 10,
        offset: int = 0,
        calc_percentage_change=False,
    ) -> Optional[OfferHistoryPagingResponse]:
        if start_time > end_time:
            raise StartTimeAfterEndTime

        statement = (
            select(Offer)
            .join(Product)
            .filter(
                and_(
                    Offer.offer_id == offer_id,
                    Offer.created_at >= start_time,
                    Offer.created_at <= end_time,
                    Product.is_deleted == false(),
                )
            )
            .order_by(Offer.created_at.asc())
        )

        results = await self.session.exec(statement)
        offers_all = results.scalars().all()

        offers = []
        for offer in offers_all:
            offers.append(
                OfferB(**offer.dict(exclude={"id", "product_id", "offer_id"}))
            )
        paging = Pagination(total_items=len(offers_all), offset=offset, limit=limit)
        if not offers:
            raise EntityDoesNotExist
        return OfferHistoryPagingResponse(
            id=offer_id,
            history=offers[offset : offset + limit]
            if not calc_percentage_change
            else offers,
            paging={
                "page": paging.page,
                "limit": paging.limit,
                "offset": paging.offset,
                "total_pages": paging.total_pages,
            },
        )
