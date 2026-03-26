from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class OrderEvent(BaseModel):
    order_id: UUID
    event_type: str
    payload: dict[str, Any]
    timestamp: datetime
