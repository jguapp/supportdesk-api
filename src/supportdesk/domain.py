from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Comment:
    author_id: str
    body: str

    def to_dict(self) -> dict[str, str]:
        return {"author_id": self.author_id, "body": self.body}


@dataclass(frozen=True, slots=True)
class Ticket:
    id: str
    organization_id: str
    requester_id: str
    subject: str
    status: str
    priority: str
    created_at: datetime
    comments: tuple[Comment, ...] = ()

    def move_to(self, status: str) -> "Ticket":
        return replace(self, status=status)

    def add_comment(self, comment: Comment) -> "Ticket":
        return replace(self, comments=(*self.comments, comment))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "subject": self.subject,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "comments": [comment.to_dict() for comment in self.comments],
        }


class TicketRepository:
    def __init__(self, tickets: list[Ticket] | None = None) -> None:
        self._tickets = {ticket.id: ticket for ticket in tickets or []}

    def get(self, ticket_id: str) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def save(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket

    def list(self) -> list[Ticket]:
        return list(self._tickets.values())

