"""Tests for the store layer."""

from datetime import date
from pathlib import Path

from tradeshow_scheduler.models import Need, Tradeshow
from tradeshow_scheduler.store import Store


def _make_store(tmp_path: Path) -> Store:
    return Store(path=tmp_path / "data.json")


def _sample_show() -> Tradeshow:
    return Tradeshow(
        name="TestShow",
        location="Chicago",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
    )


def test_add_and_load(tmp_path):
    store = _make_store(tmp_path)
    show = _sample_show()
    store.add(show)
    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].name == "TestShow"


def test_get(tmp_path):
    store = _make_store(tmp_path)
    show = _sample_show()
    store.add(show)
    found = store.get(show.id)
    assert found is not None
    assert found.name == "TestShow"
    assert store.get("nonexistent") is None


def test_update(tmp_path):
    store = _make_store(tmp_path)
    show = _sample_show()
    store.add(show)
    show.booth_number = "B99"
    show.needs.append(Need(description="Test need"))
    assert store.update(show)
    reloaded = store.get(show.id)
    assert reloaded.booth_number == "B99"
    assert len(reloaded.needs) == 1


def test_delete(tmp_path):
    store = _make_store(tmp_path)
    show = _sample_show()
    store.add(show)
    assert store.delete(show.id)
    assert store.load() == []
    assert not store.delete("nonexistent")
