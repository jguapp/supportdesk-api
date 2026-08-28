from __future__ import annotations

import json
from http import HTTPStatus

from .service import ConflictError, NotFoundError, TicketService, ValidationError


class SupportDeskApi:
    def __init__(self, service: TicketService) -> None:
        self._service = service

    def __call__(self, environ, start_response):
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/")).rstrip("/") or "/"
        organization = environ.get("HTTP_X_ORGANIZATION")
        try:
            if method == "POST" and path == "/tickets":
                ticket = self._service.create(organization, environ.get("HTTP_X_USER"), self._json(environ))
                return self._respond(start_response, HTTPStatus.CREATED, ticket.to_dict())
            if path.startswith("/tickets/"):
                suffix = path.removeprefix("/tickets/")
                if method == "PATCH" and suffix.endswith("/status"):
                    ticket_id = suffix.removesuffix("/status").rstrip("/")
                    ticket = self._service.change_status(organization, ticket_id, self._json(environ))
                    return self._respond(start_response, HTTPStatus.OK, ticket.to_dict())
                if method == "PATCH" and suffix.endswith("/assignee"):
                    ticket_id = suffix.removesuffix("/assignee").rstrip("/")
                    ticket = self._service.assign(organization, ticket_id, self._json(environ))
                    return self._respond(start_response, HTTPStatus.OK, ticket.to_dict())
                if method == "GET" and "/" not in suffix:
                    return self._respond(start_response, HTTPStatus.OK, self._service.get(organization, suffix).to_dict())
            return self._respond(start_response, HTTPStatus.NOT_FOUND, {"error": "route not found"})
        except json.JSONDecodeError:
            return self._respond(start_response, HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
        except ValidationError as error:
            return self._respond(start_response, HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except NotFoundError as error:
            return self._respond(start_response, HTTPStatus.NOT_FOUND, {"error": str(error)})
        except ConflictError as error:
            return self._respond(start_response, HTTPStatus.CONFLICT, {"error": str(error)})

    @staticmethod
    def _json(environ):
        length = int(environ.get("CONTENT_LENGTH") or 0)
        value = json.loads(environ["wsgi.input"].read(length) if length else b"{}")
        if not isinstance(value, dict):
            raise ValidationError("body must be an object")
        return value

    @staticmethod
    def _respond(start_response, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode()
        start_response(f"{status.value} {status.phrase}", [("Content-Type", "application/json")])
        return [body]

