"""Abstract stream classes for Singer Tap."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Iterator
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

LOGGER = get_logger()


class BaseStream(ABC):
    """Base abstract class for all streams."""
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
        """Unique stream ID."""

    @property
    @abstractmethod
    def replication_method(self) -> str:
        """Stream replication method."""

    @property
    @abstractmethod
    def replication_keys(self) -> List[str]:
        """Fields used for replication."""

    @property
    @abstractmethod
    def key_properties(self) -> List[str]:
        """Primary key fields."""

    def is_selected(self, _record: Optional[dict] = None) -> bool:
        """Check if stream is selected in catalog."""
        return metadata.get(self.metadata, (), "selected")

    @abstractmethod
    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        """Abstract method to sync stream."""

    def get_records(self) -> Iterator:
        """Yield paginated API records."""
        next_page = 1
        while next_page:
            response = self.client.get(
                self.url_endpoint, self.params, self.headers, self.path
            )
            raw = self.get_dot_path_value(response, self.data_key)
            
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
        """Write stream schema to stdout."""
        try:
            write_schema(self.tap_stream_id, self.schema, self.key_properties)
        except OSError as err:
            LOGGER.error("OS Error while writing schema for: %s", self.tap_stream_id)
            raise err

    def update_params(self, **kwargs) -> None:
        """Update request params for API call."""
        self.params.update(kwargs)

    def modify_object(self, record: Dict, _parent_record: Dict = None) -> Dict:
        """Override in child to modify object before writing."""
        return record

    def get_url_endpoint(self, parent_obj: Dict = None) -> str:
        """Return final API URL after formatting with parent object."""
        if parent_obj:
            try:
                formatted_path = self.path.format(**parent_obj)
            except KeyError as e:
                LOGGER.error(
                    "[%s] Missing key in parent_obj for path formatting: %s",
                    self.tap_stream_id,
                    e,
                )
                raise
        else:
            formatted_path = self.path

        full_url = f"{self.client.base_url}/{formatted_path}"
        LOGGER.info("[%s] Final URL: %s", self.tap_stream_id, full_url)
        return full_url

    def get_url_params(
        self,
        _context: Optional[Dict] = None,
        _next_page_token: Optional[str] = None,
    ) -> Dict:
        """Return default URL params. Override in child if needed."""
        return {}
    
    def get_dot_path_value(self, record: dict, dotted_path: str, default=None):
        """
        Safely retrieve a nested value from a dictionary using a dotted key path.
        """
        keys = dotted_path.split(".")
        value = record
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def append_times_to_dates(self, record: Dict) -> Dict:
        """Ensure that replication key date fields include time component."""
        for key in self.replication_keys:
            if key in record:
                val = record[key]
                if isinstance(val, str) and "T" not in val:
                    record[key] = f"{val}T00:00:00Z"
        return record


class IncrementalStream(BaseStream):
    """Base class for incremental sync streams."""
    replication_method = "INCREMENTAL"

    def get_bookmark(self, state: dict, stream: str, key: Any = None) -> int:
        """A wrapper for singer.get_bookmark to deal with compatibility for
        bookmark values or start values."""
        return get_bookmark(
            state,
            stream,
            key or self.replication_keys[0],
            self.client.config["start_date"],
        )

    def write_bookmark(self, state: dict, stream: str, key: Any = None, value: Any = None) -> Dict:
        """A wrapper for singer.get_bookmark to deal with compatibility for
        bookmark values or start values."""
        if not (key or self.replication_keys):
            return state

        current_bookmark = get_bookmark(state, stream, key or self.replication_keys[0], self.client.config["start_date"])
        value = max(current_bookmark, value)
        return write_bookmark(
            state, stream, key or self.replication_keys[0], value
        )

    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        """Sync incremental records using updatedAfter param."""
        bookmark_date = self.get_bookmark(state, self.tap_stream_id)
        current_max_bookmark_date = bookmark_date
        self.update_params(updatedAfter=bookmark_date)
        # self.update_data_payload(parent_obj=parent_obj)
        self.url_endpoint = self.get_url_endpoint(parent_obj)

        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )

                if not transformed_record:
                    LOGGER.warning("[%s] Transformed record is empty. Skipping.",
                                   self.tap_stream_id)
                    continue
                
                if self.replication_keys and transformed_record.get(self.replication_keys[0]):
                    record_bookmark = transformed_record.get(self.replication_keys[0])
                else:
                    record_bookmark = bookmark_date

                if record_bookmark >= bookmark_date:
                    if self.is_selected():
                        write_record(self.tap_stream_id, transformed_record)
                        counter.increment()

                    current_max_bookmark_date = max(
                        current_max_bookmark_date, record_bookmark
                    )

                    for child in self.child_to_sync:
                        child.sync(state=state, transformer=transformer, parent_obj=record)

            state = self.write_bookmark(state, self.tap_stream_id, value=current_max_bookmark_date)
            return counter.value


class FullTableStream(BaseStream):
    """Base class for full-table sync streams."""
    replication_method = "FULL_TABLE"

    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        """Sync all records in full-table mode."""
        self.url_endpoint = self.get_url_endpoint(parent_obj)

        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )

                if not transformed_record:
                    LOGGER.warning("[%s] Transformed record is empty. Skipping.",
                                   self.tap_stream_id)
                    continue

                if self.is_selected(record):
                    write_record(self.tap_stream_id, transformed_record)
                    counter.increment()

                for child in self.child_to_sync:
                    context = child.get_child_context(record, parent_obj)
                    if context:
                        child.sync(state=state, transformer=transformer,
                                   parent_obj=context)

        return counter.value
