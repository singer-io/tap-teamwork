from typing import Optional, Dict, Any
import singer
from singer import metrics
from tap_teamwork.streams.abstracts import BaseStream

LOGGER = singer.get_logger()


class CompanyDetails(BaseStream):
    tap_stream_id = "company_details"
    parent = "companies"
    path = "desk/api/v2/companies/{companyId}.json"

    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: list = []
    data_key = "company"

    def get_child_context(
        self, record: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return None

    def sync(self, state: Dict[str, Any], transformer: singer.Transformer, parent_obj: Dict[str, Any] = None) -> int:
        company_id = (parent_obj or {}).get("companyId") or (parent_obj or {}).get("id")
        if not company_id:
            LOGGER.warning("[%s] Missing companyId in parent_obj: %s", self.tap_stream_id, parent_obj)
            return 0

        payload = self.client.get(endpoint=None, path=self.path.format(companyId=company_id))
        record = payload.get(self.data_key) if isinstance(payload, dict) else None
        if not record:
            return 0

        with metrics.record_counter(self.tap_stream_id) as counter:
            transformed = transformer.transform(record, self.schema, self.metadata)
            if transformed:
                singer.write_record(self.tap_stream_id, transformed)
                counter.increment()
            return counter.value
