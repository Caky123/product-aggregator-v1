from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.jwt_bearer import jwtBearer
from app.db.err import EntityDoesNotExist, StartTimeAfterEndTime
from app.db.product_database import ProductDatabase
from app.db.sessions import get_database
from app.internal_models.models import (OfferHistoryPagingResponse,
                                        OfferTrendResponse)

router = APIRouter()


@router.get(
    "/offer/{offer_id}/history/{limit}/{offset}",
    tags=["offers"],
    dependencies=[Depends(jwtBearer())],
    summary="Get offer history by id.",
    description="Get offer history by id.",
    responses={
        status.HTTP_200_OK: {
            "description": "Offer history was successfully retrieved."
        },
        status.HTTP_404_NOT_FOUND: {"description": "Offer history not found"},
    },
    response_model=OfferHistoryPagingResponse,
)
async def get_offer(
    offer_id: UUID,
    limit: int = 10,
    offset: int = 0,
    database: ProductDatabase = Depends(get_database(ProductDatabase)),
) -> Optional[OfferHistoryPagingResponse]:
    try:
        return await database._get_offer_history(
            offer_id=offer_id, limit=limit, offset=offset
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer history not found."
        )


@router.get(
    "/offer/{offer_id}/trend",
    tags=["offers"],
    dependencies=[Depends(jwtBearer())],
    summary="Get offer trend.",
    description="Get offer trend.",
    responses={
        status.HTTP_200_OK: {"description": "Offer trend was successfully retrieved."},
        status.HTTP_400_BAD_REQUEST: {"description": "Start time after end time."},
        status.HTTP_404_NOT_FOUND: {"description": "Offer history not found."},
    },
    response_model=OfferTrendResponse,
)
async def get_offer_trend(
    offer_id: UUID,
    start_time: datetime = datetime.utcnow(),
    end_time: datetime =  datetime.utcnow(),
    database: ProductDatabase = Depends(get_database(ProductDatabase)),
) -> Optional[OfferTrendResponse]:
    try:
        offer_history = await database._get_offer_history(
            offer_id=offer_id,
            start_time=start_time,
            end_time=end_time,
            calc_percentage_change=True,
        )

        if offer_history.history:
            last_val = offer_history.history[-1].price
            first_val = offer_history.history[0].price
            percentage_change = ((last_val - first_val) / first_val) * 100

            return OfferTrendResponse(
                id=offer_history.id,
                history=offer_history.history,
                price_trend=f"{percentage_change:.2f}",
            )
        else:
            raise EntityDoesNotExist
    except StartTimeAfterEndTime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Start time after end time."
        )
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer history not found."
        )
