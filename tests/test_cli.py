"""Tests for the CLI interface."""

from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from tradeshow_scheduler.cli import main
from tradeshow_scheduler.store import Store


@pytest.fixture
def store(tmp_path):
    s = Store(path=tmp_path / "data.json")
    with patch("tradeshow_scheduler.cli.Store", return_value=s):
        yield s


def test_add_and_list(store, capsys):
    future = (date.today() + timedelta(days=30)).isoformat()
    future_end = (date.today() + timedelta(days=32)).isoformat()
    main(["add", "TestExpo", "Denver", future, future_end, "--booth", "C1"])
    out = capsys.readouterr().out
    assert "Added tradeshow 'TestExpo'" in out

    main(["list"])
    out = capsys.readouterr().out
    assert "TestExpo" in out
    assert "Denver" in out


def test_add_validates_dates(store):
    with pytest.raises(SystemExit):
        main(["add", "Bad", "Nowhere", "2026-06-10", "2026-06-01"])


def test_show_details(store, capsys):
    main(["add", "DetailShow", "Austin", "2026-09-01", "2026-09-03"])
    shows = store.load()
    show_id = shows[0].id

    main(["show", show_id])
    out = capsys.readouterr().out
    assert "DetailShow" in out
    assert "Austin" in out


def test_delete(store, capsys):
    main(["add", "ToDelete", "LA", "2026-10-01", "2026-10-02"])
    shows = store.load()
    show_id = shows[0].id

    main(["delete", show_id])
    out = capsys.readouterr().out
    assert "Deleted" in out
    assert store.load() == []


def test_add_and_complete_need(store, capsys):
    main(["add", "NeedShow", "SF", "2026-11-01", "2026-11-03"])
    show_id = store.load()[0].id

    main(["add-need", show_id, "Print flyers", "-p", "high", "-a", "Bob"])
    out = capsys.readouterr().out
    assert "Added need" in out

    need_id = store.load()[0].needs[0].id
    main(["complete-need", show_id, need_id])
    out = capsys.readouterr().out
    assert "completed" in out


def test_remove_need(store, capsys):
    main(["add", "RmNeed", "Portland", "2026-12-01", "2026-12-02"])
    show_id = store.load()[0].id
    main(["add-need", show_id, "Book hotel"])
    need_id = store.load()[0].needs[0].id

    main(["remove-need", show_id, need_id])
    out = capsys.readouterr().out
    assert "Removed need" in out
    assert len(store.load()[0].needs) == 0
