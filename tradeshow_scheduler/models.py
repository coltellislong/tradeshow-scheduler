"""Data models for tradeshow scheduling."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class NeedStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class NeedPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Need:
    description: str
    status: NeedStatus = NeedStatus.PENDING
    priority: NeedPriority = NeedPriority.MEDIUM
    assignee: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee": self.assignee,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Need:
        return cls(
            id=data["id"],
            description=data["description"],
            status=NeedStatus(data["status"]),
            priority=NeedPriority(data["priority"]),
            assignee=data.get("assignee", ""),
        )


@dataclass
class Tradeshow:
    name: str
    location: str
    start_date: date
    end_date: date
    booth_number: str = ""
    notes: str = ""
    needs: list[Need] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    @property
    def days_until(self) -> int:
        return (self.start_date - date.today()).days

    @property
    def is_upcoming(self) -> bool:
        return self.start_date >= date.today()

    @property
    def pending_needs(self) -> list[Need]:
        return [n for n in self.needs if n.status != NeedStatus.COMPLETED]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "booth_number": self.booth_number,
            "notes": self.notes,
            "needs": [n.to_dict() for n in self.needs],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Tradeshow:
        return cls(
            id=data["id"],
            name=data["name"],
            location=data["location"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            booth_number=data.get("booth_number", ""),
            notes=data.get("notes", ""),
            needs=[Need.from_dict(n) for n in data.get("needs", [])],
        )
