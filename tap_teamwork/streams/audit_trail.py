from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class AuditTrail(FullTableStream):
    tap_stream_id = "audit_trail"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "audit_trail"
    path = "audit_trail"
