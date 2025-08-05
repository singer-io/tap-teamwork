from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from singer import (
    Transformer,
    get_bookmark,
    get_logger,
    metrics,
    write_bookmark,
    write_record,
    write_schema,
    metadata
)
from datetime import datetime

LOGGER = get_logger()

class BaseStream(ABC):
    url_endpoint = ""
    path = ""
    page_size = 0
    next_page_key = ""
    headers = {'Accept': 'application/json'}
    children = []
    parent = ""
    data_key = ""
    parent_bookmark_key = ""

    def __init__(self, client=None, catalog=None) -> None:
        self.client = client
        self.catalog = catalog
        self.schema = catalog.schema.to_dict() if catalog else {}
        self.metadata = metadata.to_map(catalog.metadata) if catalog else {}
        self.child_to_sync = []
        self.params = {}

    @property
    @abstractmethod
    def tap_stream_id(self) -> str:
        pass

    @property
    @abstractmethod
    def replication_method(self) -> str:
        pass

    @property
    @abstractmethod
    def replication_keys(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def key_properties(self) -> List[str]:
        pass

    def is_selected(self, record: Optional[dict] = None) -> bool:
        return metadata.get(self.metadata, (), "selected")

    @abstractmethod
    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        pass

    def get_records(self) -> List:
        next_page = 1
        while next_page:
            response = self.client.get(
                self.url_endpoint, self.params, self.headers, self.path
            )
            raw = response.get(self.data_key, [])
            if isinstance(raw, dict):
                raw_records = [raw]
            elif isinstance(raw, list):
                raw_records = raw
            else:
                raw_records = []

            next_page = response.get(self.next_page_key)
            if next_page:
                self.params[self.next_page_key] = next_page
            else:
                self.params.pop(self.next_page_key, None)

            yield from raw_records

    def write_schema(self) -> None:
        try:
            write_schema(self.tap_stream_id, self.schema, self.key_properties)
        except OSError as err:
            LOGGER.error(f"OS Error while writing schema for: {self.tap_stream_id}")
            raise err

    def update_params(self, **kwargs) -> None:
        self.params.update(kwargs)

    def modify_object(self, record: Dict, parent_record: Dict = None) -> Dict:
        return record

    def get_url_endpoint(self, parent_obj: Dict = None) -> str:
        if parent_obj:
            try:
                formatted_path = self.path.format(**parent_obj)
            except KeyError as e:
                LOGGER.error(f"[{self.tap_stream_id}] Missing key in parent_obj for path formatting: {e}")
                raise
        else:
            formatted_path = self.path

        full_url = f"{self.client.base_url}/{formatted_path}"
        LOGGER.info(f"[{self.tap_stream_id}] Final URL: {full_url}")
        return full_url


class IncrementalStream(BaseStream):
    replication_method = "INCREMENTAL"

    def get_starting_timestamp(self, state: dict) -> Optional[str]:
        """Get ISO8601 bookmark or fallback to start_date."""
        bookmark = get_bookmark(state, self.tap_stream_id, self.replication_keys[0])
        if not bookmark:
            bookmark = self.client.config.get("start_date")
        return bookmark

    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        self.url_endpoint = self.get_url_endpoint(parent_obj)

        # Attach updatedAfter if supported
        start_value = self.get_starting_timestamp(state)
        if start_value:
            self.params["updatedAfter"] = start_value

        latest_value = start_value

        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )

                if not transformed_record:
                    LOGGER.warning(f"[{self.tap_stream_id}] Transformed record is empty. Skipping.")
                    continue

                if self.is_selected(record):
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()

                # Track latest bookmark value
                updated_at = record.get(self.replication_keys[0])
                if updated_at and (latest_value is None or updated_at > latest_value):
                    latest_value = updated_at

                # Trigger children
                for child in self.child_to_sync:
                    context = child.get_child_context(record, parent_obj)
                    if context:
                        child.sync(state=state, transformer=transformer, parent_obj=context)

        # Update bookmark
        if latest_value:
            write_bookmark(state, self.tap_stream_id, self.replication_keys[0], latest_value)

        return counter.value


class FullTableStream(BaseStream):
    replication_method = "FULL_TABLE"

    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        self.url_endpoint = self.get_url_endpoint(parent_obj)

        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )

                if not transformed_record:
                    LOGGER.warning(f"[{self.tap_stream_id}] Transformed record is empty. Skipping.")
                    continue

                if self.is_selected(record):
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()

                for child in self.child_to_sync:
                    context = child.get_child_context(record, parent_obj)
                    if context:
                        child.sync(state=state, transformer=transformer, parent_obj=context)

        return counter.value
