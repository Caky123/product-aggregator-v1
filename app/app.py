import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select
from sqlalchemy.sql.expression import false

from app.db.sessions import async_engine, create_tables
from app.db.tables.offers import Offer
from app.db.tables.products import Product
from app.external_service.offer_handler import get_product_offers
from app.settings.conf import settings

from .router import offers, products, token

logger = logging.getLogger()


async def update_offers():
    while True:
        logger.info("Periodically job starting. Check offers..")
        statement = select(Product).filter(Product.is_deleted == false())
        async with async_engine.connect() as conn:
            result = await conn.execute(statement)

            for product in result.fetchall():
                product_id = product[0]
                logger.info(f"Check offer for productId <{product_id}>")
                response_product_offers = await get_product_offers(id=product_id)

                response_status = response_product_offers.get("status_code")
                response_data = response_product_offers.get("data", [{}])
                if response_status != status.HTTP_200_OK:
                    logger.error(
                        f"Offer update failed <{response_status}>, <{response_data}>,"
                    )
                    return
                for offer in response_data:
                    if offer:
                        offer_id = offer.get("id")
                        price = offer.get("price")
                        items_in_stock = offer.get("items_in_stock")
                        logger.info(
                            f"Offer id <{offer_id}>, price <{price}>, \
                                items in stock <{items_in_stock}>, productId <{product_id}>"
                        )
                        stmt = insert(Offer).values(
                            price=price,
                            items_in_stock=items_in_stock,
                            offer_id=offer_id,
                            product_id=product_id,
                        )
                        result = await conn.execute(stmt)
                        await conn.commit()
        await async_engine.dispose()
        await asyncio.sleep(settings.offer_job_period)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    asyncio.create_task(update_offers())
    yield


def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        docs_url="/docs",
        lifespan=lifespan,
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Not authenticated."},
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "description": "Internal server error."
            },
        },
        swagger_ui_parameters={"filters": True},
    )

    @app.exception_handler(Exception)
    async def base_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Welcome to product microservice!"}

    app.include_router(products.router, prefix=settings.api_prefix)
    app.include_router(offers.router, prefix=settings.api_prefix)
    app.include_router(token.router, prefix=settings.api_prefix)
    return app
