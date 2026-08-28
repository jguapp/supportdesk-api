from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from .domain import Comment, Ticket, TicketRepository


class ConflictError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


TRANSITIONS = {
    "open": {"pending", "resolved"},
    "pending": {"open", "resolved"},
    "resolved": {"open"},
}


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        *,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._repository = repository
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._id_factory = id_factory or (lambda: str(uuid4()))

    def create(self, organization_id: object, requester_id: object, data: dict[str, object]) -> Ticket:
        organization = self._text(organization_id, "X-Organization")
        requester = self._text(requester_id, "X-User")
        subject = self._text(data.get("subject"), "subject")
        priority = data.get("priority", "normal")
        if priority not in {"low", "normal", "high", "urgent"}:
            raise ValidationError("priority is invalid")
        ticket = Ticket(self._id_factory(), organization, requester, subject, "open", priority, self._clock())
        self._repository.save(ticket)
        return ticket

    def get(self, organization_id: object, ticket_id: str) -> Ticket:
        organization = self._text(organization_id, "X-Organization")
        ticket = self._repository.get(ticket_id)
        if ticket is None or ticket.organization_id != organization:
            raise NotFoundError("ticket was not found")
        return ticket

    def change_status(self, organization_id: object, ticket_id: str, data: dict[str, object]) -> Ticket:
        ticket = self.get(organization_id, ticket_id)
        status = data.get("status")
        if status not in TRANSITIONS[ticket.status]:
            raise ConflictError(f"cannot move ticket from {ticket.status} to {status}")
        updated = ticket.move_to(status)
        self._repository.save(updated)
        return updated

    def add_comment(self, organization_id: object, ticket_id: str, data: dict[str, object]) -> Ticket:
        ticket = self.get(organization_id, ticket_id)
        author = self._text(data.get("author_id"), "author_id")
        body = self._text(data.get("body"), "body")
        updated = ticket.add_comment(Comment(author, body))
        self._repository.save(updated)
        return updated

    @staticmethod
    def _text(value: object, name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{name} is required")
        return value.strip()

