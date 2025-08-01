from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()

class Tickets(FullTableStream):
    tap_stream_id = "tickets"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "tickets"
    path = "desk/v2/tickets.json"

    #This line is added to register child streams
    children = ["ticket_details"]
