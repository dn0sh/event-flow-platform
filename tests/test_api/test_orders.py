from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.routes import orders as orders_module
from src.models.schemas import OrderCreate, OrderUpdateStatus


class _Rows:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _ExecResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return _Rows(self._items)


class FakeSession:
    def __init__(self, items):
        self.items = {item.id: item for item in items}
        self._added = None

    def add(self, order):
        self._added = order

    async def commit(self):
        if self._added is not None and self._added.id not in self.items:
            self.items[self._added.id] = self._added

    async def refresh(self, order):
        now = datetime.now(timezone.utc)
        if getattr(order, "id", None) is None:
            order.id = uuid4()
        if getattr(order, "status", None) is None:
            order.status = "pending"
        if getattr(order, "created_at", None) is None:
            order.created_at = now
        if getattr(order, "updated_at", None) is None:
            order.updated_at = now
        return None

    async def scalar(self, _query):
        return len(self.items)

    async def execute(self, _query):
        return _ExecResult(list(self.items.values()))

    async def get(self, _model, order_id):
        return self.items.get(order_id)


def _order(status: str = "pending"):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        customer_id="c-1",
        description="demo",
        amount=10.5,
        status=status,
        is_vip=False,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_order_unit(fake_redis):
    orders_module.redis_service = fake_redis
    session = FakeSession([])
    payload = OrderCreate(customer_id="c-1", description="demo", amount=10.5, is_vip=False)
    created = await orders_module.create_order(payload, session)
    assert created.customer_id == "c-1"


@pytest.mark.asyncio
async def test_list_orders_unit(fake_redis):
    orders_module.redis_service = fake_redis
    session = FakeSession([_order()])
    result = await orders_module.list_orders(20, 0, session)
    assert result.total == 1
    assert len(result.items) == 1


@pytest.mark.asyncio
async def test_get_order_from_cache_unit(fake_redis):
    item = _order()
    fake_redis.cache[str(item.id)] = orders_module._to_order_read(item).model_dump_json()
    orders_module.redis_service = fake_redis
    session = FakeSession([])
    result = await orders_module.get_order(item.id, session)
    assert result.id == item.id


@pytest.mark.asyncio
async def test_get_order_not_found_unit(fake_redis):
    orders_module.redis_service = fake_redis
    session = FakeSession([])
    with pytest.raises(HTTPException):
        await orders_module.get_order(uuid4(), session)


@pytest.mark.asyncio
async def test_patch_status_and_cancel_unit(fake_redis):
    item = _order()
    orders_module.redis_service = fake_redis
    session = FakeSession([item])
    patched = await orders_module.patch_order_status(
        item.id, OrderUpdateStatus(status="processing"), session
    )
    assert patched.status == "processing"
    await orders_module.cancel_order(item.id, session)
