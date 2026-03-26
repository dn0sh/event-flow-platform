from datetime import datetime, timezone
from uuid import uuid4

from src.models.event import OrderEvent


def test_order_event_model():
    payload = OrderEvent(
        order_id=uuid4(),
        event_type="status.changed",
        payload={"status": "processing"},
        timestamp=datetime.now(timezone.utc),
    )
    assert payload.event_type == "status.changed"
