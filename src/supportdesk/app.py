from wsgiref.simple_server import make_server

from .api import SupportDeskApi
from .domain import TicketRepository
from .service import TicketService


if __name__ == "__main__":
    app = SupportDeskApi(TicketService(TicketRepository()))
    with make_server("127.0.0.1", 8007, app) as server:
        server.serve_forever()

