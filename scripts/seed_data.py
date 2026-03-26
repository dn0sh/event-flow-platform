from __future__ import annotations

import asyncio
import random

from sqlalchemy import insert

from src.models.order import Order
from src.services.postgres_service import session_factory


async def seed_orders(count: int = 100) -> None:
    async with session_factory() as session:
        rows = []
        for i in range(count):
            rows.append(
                {
                    "customer_id": f"demo-customer-{i % 10}",
                    "description": f"Demo order #{i}",
                    "amount": round(random.uniform(10.0, 500.0), 2),
                    "status": random.choice(["pending", "processing", "completed"]),
                    "is_vip": i % 15 == 0,
                }
            )
        await session.execute(insert(Order), rows)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_orders())
