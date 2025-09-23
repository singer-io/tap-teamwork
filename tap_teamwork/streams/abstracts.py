"""Abstract stream classes for Singer Tap."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Iterator

from singer import (
    Transformer,
    get_bookmark,
    get_logger,
    metrics,
    write_bookmark,
    write_record,
    write_schema,
    metadata,
)

LOGGER = get_logger()


class BaseStream(ABC):
    """Base abstract class for all streams."""

    url_endpoint = ""
    path = ""
    page_size = 0
    next_page_key = ""
    headers = {"Accept": "application/json"}
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
        """Safely retrieve a nested value from a dictionary using a dotted key path."""
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

    def get_starting_timestamp(self, _context: Optional[Dict] = None) -> str:
        """Return the starting timestamp from config, or fallback epoch."""
        cfg = getattr(self.client, "config", {}) or {}
        return cfg.get("start_date", "1970-01-01T00:00:00Z")


class IncrementalStream(BaseStream):
    """Base class for incremental sync streams."""

    replication_method = "INCREMENTAL"

    @staticmethod
    def _minus_one_second_iso8601(ts: str) -> str:
        """Return timestamp minus one second as ISO8601 Zulu."""
        fmt_candidates = ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ")
        last_exc = None
        for fmt in fmt_candidates:
            try:
                dt = datetime.strptime(ts, fmt)
                dt = dt.replace(tzinfo=timezone.utc) - timedelta(seconds=1)
                return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError as exc:
                last_exc = exc
        raise ValueError(
            f"Bookmark '{ts}' is not a supported ISO8601 Zulu timestamp"
        ) from last_exc

    def _parse_utc(self, ts: Optional[str]) -> Optional[datetime]:
        if not ts:
            return None
        try:
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        return dt.replace(tzinfo=timezone.utc)

    def get_bookmark(self, state: dict, stream: str, key: Any = None) -> str:
        """Singer get_bookmark wrapper honoring start_date fallback."""
        return get_bookmark(
            state,
            stream,
            key or self.replication_keys[0],
            self.client.config["start_date"],
        )

    def write_bookmark(
        self, state: dict, stream: str, key: Any = None, value: Any = None
    ) -> Dict:
        """Singer write_bookmark wrapper that advances monotonically."""
        if not (key or self.replication_keys):
            return state
        current_bookmark = get_bookmark(
            state,
            stream,
            key or self.replication_keys[0],
            self.client.config["start_date"],
        )
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
        """Incremental sync with strict bookmark filtering and real counting."""

        bookmark_str = self.get_bookmark(state, self.tap_stream_id)
        bookmark_dt = self._parse_utc(bookmark_str)
        max_seen_dt = bookmark_dt

        # Apply -1s shift for the request param, if we have a bookmark.
        if bookmark_str:
            try:
                shifted = self._minus_one_second_iso8601(bookmark_str)
                self.update_params(updatedAfter=shifted)
            except ValueError:
                LOGGER.warning(
                    "[%s] Could not parse bookmark '%s'; using it as-is",
                    self.tap_stream_id,
                    bookmark_str,
                )
                self.update_params(updatedAfter=bookmark_str)

        self.url_endpoint = self.get_url_endpoint(parent_obj)

        written = 0
        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )
                if transformed_record is None:
                    LOGGER.warning(
                        "[%s] Transformed record is None. Skipping.",
                        self.tap_stream_id,
                    )
                    continue

                rk = self.replication_keys[0] if self.replication_keys else None
                rec_dt = self._parse_utc(transformed_record.get(rk)) if rk else None

                # STRICT filter: only accept strictly newer records
                if bookmark_dt and rec_dt and rec_dt <= bookmark_dt:
                    continue

                if self.is_selected():
                    write_record(self.tap_stream_id, transformed_record)
                    written += 1
                    counter.increment()

                if rec_dt and (max_seen_dt is None or rec_dt > max_seen_dt):
                    max_seen_dt = rec_dt

                for child in self.child_to_sync:
                    child.sync(
                        state=state,
                        transformer=transformer,
                        parent_obj=record,
                    )

        if max_seen_dt:
            state = self.write_bookmark(
                state,
                self.tap_stream_id,
                value=max_seen_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        LOGGER.info("FINISHED Syncing: %s, total_records: %d",
                    self.tap_stream_id, written)
        return written


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

        written = 0
        with metrics.record_counter(self.tap_stream_id) as counter:
            for record in self.get_records():
                transformed_record = transformer.transform(
                    record, self.schema, self.metadata
                )
                if transformed_record is None:
                    LOGGER.warning("[%s] Transformed record is None. Skipping.",
                                   self.tap_stream_id)
                    continue

                if self.is_selected(record):
                    write_record(self.tap_stream_id, transformed_record)
                    written += 1
                    counter.increment()

                for child in self.child_to_sync:
                    context = child.get_child_context(record, parent_obj)
                    if context:
                        child.sync(
                            state=state,
                            transformer=transformer,
                            parent_obj=context,
                        )

        LOGGER.info("FINISHED Syncing: %s, total_records: %d",
                    self.tap_stream_id, written)
        return written
