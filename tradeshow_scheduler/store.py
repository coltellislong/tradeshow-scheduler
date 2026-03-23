"""JSON file-based storage for tradeshows."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Tradeshow

DEFAULT_PATH = Path.home() / ".tradeshow-scheduler" / "data.json"


class Store:
    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = path

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]")

    def load(self) -> list[Tradeshow]:
        self._ensure_file()
        data = json.loads(self.path.read_text())
        return [Tradeshow.from_dict(d) for d in data]

    def save(self, tradeshows: list[Tradeshow]) -> None:
        self._ensure_file()
        data = [t.to_dict() for t in tradeshows]
        self.path.write_text(json.dumps(data, indent=2) + "\n")

    def get(self, show_id: str) -> Tradeshow | None:
        for show in self.load():
            if show.id == show_id:
                return show
        return None

    def add(self, show: Tradeshow) -> None:
        shows = self.load()
        shows.append(show)
        self.save(shows)

    def update(self, show: Tradeshow) -> bool:
        shows = self.load()
        for i, s in enumerate(shows):
            if s.id == show.id:
                shows[i] = show
                self.save(shows)
                return True
        return False

    def delete(self, show_id: str) -> bool:
        shows = self.load()
        filtered = [s for s in shows if s.id != show_id]
        if len(filtered) == len(shows):
            return False
        self.save(filtered)
        return True
