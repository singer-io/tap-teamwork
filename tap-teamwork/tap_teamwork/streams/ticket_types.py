from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class TicketTypes(FullTableStream):
    tap_stream_id = "ticket_types"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "types"
    path = "desk/api/v2/search/tickets.json"
