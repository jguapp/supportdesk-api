import unittest
from datetime import datetime, timezone

from supportdesk.domain import TicketRepository
from supportdesk.service import ConflictError, NotFoundError, TicketService, ValidationError


NOW = datetime(2026, 8, 28, tzinfo=timezone.utc)


class TicketServiceTests(unittest.TestCase):
    def setUp(self):
        self.repo = TicketRepository()
        self.service = TicketService(self.repo, clock=lambda: NOW, id_factory=lambda: "t1")
        self.service.create("org1", "u1", {"subject": "Cannot log in", "priority": "high"})

    def test_ticket_is_scoped_to_organization(self):
        self.assertEqual("t1", self.service.get("org1", "t1").id)
        with self.assertRaises(NotFoundError):
            self.service.get("org2", "t1")

    def test_valid_transition_is_persisted(self):
        ticket = self.service.change_status("org1", "t1", {"status": "pending"})
        self.assertEqual("pending", ticket.status)
        self.assertEqual("pending", self.repo.get("t1").status)

    def test_invalid_transition_is_rejected(self):
        self.service.change_status("org1", "t1", {"status": "resolved"})
        with self.assertRaises(ConflictError):
            self.service.change_status("org1", "t1", {"status": "pending"})

    def test_unknown_priority_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.create("org1", "u1", {"subject": "Help", "priority": "now"})

    def test_ticket_can_be_assigned(self):
        ticket = self.service.assign("org1", "t1", {"assignee_id": "agent-2"})
        self.assertEqual("agent-2", ticket.assignee_id)


if __name__ == "__main__":
    unittest.main()
