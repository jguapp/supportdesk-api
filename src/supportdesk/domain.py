from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Ticket:
    id: str
    organization_id: str
    requester_id: str
    subject: str
    status: str
    priority: str
    created_at: datetime
    assignee_id: str | None = None

    def move_to(self, status: str) -> "Ticket":
        return replace(self, status=status)

    def assign_to(self, assignee_id: str | None) -> "Ticket":
        return replace(self, assignee_id=assignee_id)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "subject": self.subject,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "assignee_id": self.assignee_id,
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
