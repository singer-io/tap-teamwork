from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class TicketNotes(FullTableStream):
    tap_stream_id = "ticket_notes"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "ticket_notes"
    path = "ticket_notes"
