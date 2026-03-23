"""Tests for data models."""

from datetime import date, timedelta

from tradeshow_scheduler.models import Need, NeedPriority, NeedStatus, Tradeshow


def test_need_round_trip():
    need = Need(description="Order banners", priority=NeedPriority.HIGH, assignee="Alice")
    data = need.to_dict()
    restored = Need.from_dict(data)
    assert restored.description == need.description
    assert restored.priority == NeedPriority.HIGH
    assert restored.assignee == "Alice"
    assert restored.id == need.id


def test_tradeshow_round_trip():
    show = Tradeshow(
        name="CES 2026",
        location="Las Vegas",
        start_date=date(2026, 1, 7),
        end_date=date(2026, 1, 10),
        booth_number="A42",
        notes="Bring demo units",
        needs=[Need(description="Ship hardware")],
    )
    data = show.to_dict()
    restored = Tradeshow.from_dict(data)
    assert restored.name == "CES 2026"
    assert restored.booth_number == "A42"
    assert len(restored.needs) == 1
    assert restored.needs[0].description == "Ship hardware"


def test_tradeshow_upcoming():
    future = date.today() + timedelta(days=30)
    show = Tradeshow(
        name="Future Show",
        location="NYC",
        start_date=future,
        end_date=future + timedelta(days=2),
    )
    assert show.is_upcoming
    assert show.days_until == 30


def test_tradeshow_past():
    past = date.today() - timedelta(days=10)
    show = Tradeshow(
        name="Past Show",
        location="LA",
        start_date=past,
        end_date=past + timedelta(days=2),
    )
    assert not show.is_upcoming


def test_pending_needs():
    show = Tradeshow(
        name="Test",
        location="Here",
        start_date=date.today(),
        end_date=date.today(),
        needs=[
            Need(description="A", status=NeedStatus.PENDING),
            Need(description="B", status=NeedStatus.COMPLETED),
            Need(description="C", status=NeedStatus.IN_PROGRESS),
        ],
    )
    assert len(show.pending_needs) == 2
