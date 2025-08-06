from typing import Optional, Iterable, Any, Dict
from singer import get_logger, write_record, write_schema, Transformer, metrics
from tap_teamwork.streams.abstracts import BaseStream
from tap_teamwork.streams.companies import Companies

LOGGER = get_logger()

class CompanyDetails(BaseStream):
    tap_stream_id = "company_details"
    path = "desk/api/v2/companies/{companyId}.json"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: list = []
    parent = "companies"
    data_key = "company"

    parent_stream_type = Companies
    ignore_parent_replication_keys = True

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        return {}

    def get_child_context(self, record: dict, context: Optional[dict]) -> Optional[dict]:
        return {"companyId": record.get("id")}

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        company_id = context.get("companyId") if context else None

        if not company_id or not isinstance(company_id, int) or company_id < 1:
            LOGGER.warning(f"Skipping company_details due to invalid companyId: {company_id}")
            return []
        final_url = self.get_url_endpoint({"companyId": company_id})
        LOGGER.info(f"[company_details] Fetching from URL: {final_url}")


        try:
            response = self.client.get(self.get_url_endpoint({"companyId": company_id}))
            if response:
                return [response]
        except Exception as ex:
            LOGGER.warning(f"Failed to fetch company_details for ID={company_id}. Error: {ex}")
            return []

        return []

    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        self.url_endpoint = self.get_url_endpoint(parent_obj)

        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records(parent_obj):
                transformed = transformer.transform(record, self.schema, self.metadata)

                if transformed:
                    write_record(self.tap_stream_id, transformed)
                    counter.increment()
                else:
                    LOGGER.warning(f"[{self.tap_stream_id}] Empty transformed record, skipping.")

        return counter.value
