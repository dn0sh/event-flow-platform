from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


OrderStatus = Literal["pending", "processing", "completed", "cancelled"]


class OrderCreate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=1024)
    amount: float = Field(gt=0)
    is_vip: bool = False


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class OrderRead(BaseModel):
    id: UUID
    customer_id: str
    description: str
    amount: float
    status: OrderStatus
    is_vip: bool
    created_at: datetime
    updated_at: datetime


class PaginatedOrders(BaseModel):
    items: list[OrderRead]
    total: int
    limit: int
    offset: int
