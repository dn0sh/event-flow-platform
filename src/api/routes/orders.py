from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.order import Order
from src.models.schemas import (
    OrderCreate,
    OrderRead,
    OrderStatus,
    OrderUpdateStatus,
    PaginatedOrders,
)
from src.services.postgres_service import get_db_session
from src.services.redis_service import redis_service
from src.utils.metrics import order_status_updates_total, orders_created_total

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_order_read(order: Order) -> OrderRead:
    order_id = order.id if isinstance(order.id, UUID) else UUID(str(order.id))
    status = cast(OrderStatus, order.status)
    return OrderRead(
        id=order_id,
        customer_id=order.customer_id,
        description=order.description,
        amount=order.amount,
        status=status,
        is_vip=order.is_vip,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate, session: AsyncSession = Depends(get_db_session)
) -> OrderRead:
    order = Order(**payload.model_dump())
    session.add(order)
    await session.commit()
    await session.refresh(order)
    orders_created_total.inc()
    return _to_order_read(order)


@router.get("", response_model=PaginatedOrders)
async def list_orders(
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedOrders:
    total = await session.scalar(select(func.count()).select_from(Order))
    query = select(Order).order_by(Order.created_at.desc()).limit(limit).offset(offset)
    rows = (await session.execute(query)).scalars().all()
    return PaginatedOrders(
        items=[_to_order_read(item) for item in rows],
        total=int(total or 0),
        limit=limit,
        offset=offset,
    )


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: UUID, session: AsyncSession = Depends(get_db_session)) -> OrderRead:
    cached = await redis_service.get_cached_order(str(order_id))
    if cached:
        return OrderRead.model_validate_json(cached)

    row = await session.get(Order, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    response = _to_order_read(row)
    await redis_service.set_cached_order(str(order_id), response.model_dump_json())
    return response


@router.patch("/{order_id}/status", response_model=OrderRead)
async def patch_order_status(
    order_id: UUID, payload: OrderUpdateStatus, session: AsyncSession = Depends(get_db_session)
) -> OrderRead:
    row = await session.get(Order, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")

    row.status = payload.status
    await session.commit()
    await session.refresh(row)
    await redis_service.invalidate_order(str(order_id))
    order_status_updates_total.inc()
    return _to_order_read(row)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: UUID, session: AsyncSession = Depends(get_db_session)) -> None:
    row = await session.get(Order, order_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    await session.execute(delete(Order).where(Order.id == order_id))
    await session.commit()
    await redis_service.invalidate_order(str(order_id))
