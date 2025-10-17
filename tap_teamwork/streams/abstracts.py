"""Abstract stream classes for Singer Tap."""

from abc import ABC, abstractmethod
from datetime import timedelta
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
    utils,
)

LOGGER = get_logger()


class BaseStream(ABC):
    """Base abstract class for all streams."""

    url_endpoint = ""
    path = ""
    page_size = 0
    next_page_key = ""
    headers = {"Accept": "application/json"}
    children: List[Any] = []
    parent = ""
    data_key = ""
    parent_bookmark_key = ""

    # Default query param for incremental window; override in child if needed.
    replication_key_param = "updatedAfter"

    def __init__(self, client=None, catalog=None) -> None:
        self.client = client
        self.catalog = catalog
        self.schema = catalog.schema.to_dict() if catalog else {}
        self.metadata = metadata.to_map(catalog.metadata) if catalog else {}
        self.child_to_sync: List[Any] = []
        self.params: Dict[str, Any] = {}

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

            for r in raw_records:
                yield r

    def write_schema(self) -> None:
        """Write stream schema to stdout."""
        try:
            write_schema(self.tap_stream_id, self.schema, self.key_properties)
        except OSError as err:
            LOGGER.error("OS error while writing schema for: %s", self.tap_stream_id)
            raise err

    def update_params(self, **kwargs) -> None:
        """Update request params for API call."""
        self.params.update(kwargs)

    def modify_object(self, record: Dict, parent_record: Dict = None) -> Dict:
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

        full_url = self.client.build_url(formatted_path)
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

    def _parse_utc(self, ts: Optional[str]):
        """Parse RFC3339/ISO8601 into aware UTC datetime, nil/invalid-safe."""
        if ts is None:
            return None
        if isinstance(ts, str) and ts.strip().lower() in ("", "null", "none"):
            return None
        try:
            return utils.strptime_to_utc(ts)
        except Exception:
            return None

    def _fmt(self, dt) -> str:
        """Format datetime into RFC3339 with Z."""
        return utils.strftime(dt)

    def _minus_one_second_str(self, ts: str) -> Optional[str]:
        """Return (ts - 1s) as RFC3339 string; None if ts invalid."""
        dt = self._parse_utc(ts)
        if not dt:
            return None
        # Trim micros for safer server filtering (optional but common)
        dt = (dt - timedelta(seconds=1)).replace(microsecond=0)
        return self._fmt(dt)

    # ---------- State helpers (compare datetimes, not strings) ----------
    def get_bookmark(self, state: dict, stream: str, key: Any = None) -> str:
        """Bookmark with start_date fallback."""
        return get_bookmark(
            state,
            stream,
            key or self.replication_keys[0],
            self.client.config.get("start_date", "1970-01-01T00:00:00Z"),
        )

    def write_bookmark(
        self, state: dict, stream: str, key: Any = None, value: Any = None
    ) -> Dict:
        """Advance bookmark to the max(datetime(current, value))."""
        if not (key or self.replication_keys):
            return state

        rk = key or self.replication_keys[0]
        current = get_bookmark(
            state, stream, rk, self.client.config.get("start_date", "1970-01-01T00:00:00Z")
        )

        cur_dt = self._parse_utc(current) if current else None
        new_dt = self._parse_utc(value) if isinstance(value, str) else value

        if cur_dt and new_dt:
            chosen = cur_dt if cur_dt > new_dt else new_dt
        else:
            chosen = new_dt or cur_dt

        if chosen:
            return write_bookmark(state, stream, rk, self._fmt(chosen))
        return state

    # ---------- Sync ----------
    def sync(
        self,
        state: Dict,
        transformer: Transformer,
        parent_obj: Dict = None,
    ) -> Dict:
        """Incremental sync with inclusive boundary and correct state writes."""
        rk = self.replication_keys[0] if self.replication_keys else None

        # Resolve bookmark (or start_date) and compute request param (bookmark - 1s)
        bookmark_str = self.get_bookmark(state, self.tap_stream_id, rk)
        bookmark_dt = self._parse_utc(bookmark_str) if bookmark_str else None
        max_seen_dt = bookmark_dt

        shifted = self._minus_one_second_str(bookmark_str) if bookmark_str else None
        if shifted:
            key_param = getattr(self, "replication_key_param", "updatedAfter")
            self.update_params(**{key_param: shifted})

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

                # Parse replication key value (nil-safe)
                rec_val = transformed_record.get(rk) if rk else None
                rec_dt = self._parse_utc(rec_val) if rec_val else None

                # INCLUSIVE boundary: skip only records strictly OLDER than bookmark.
                # If rec_dt is None, we keep the record but it won't advance the bookmark.
                if bookmark_dt and rec_dt is not None and rec_dt < bookmark_dt:
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
                rk,
                max_seen_dt,  # pass datetime; formatter handles to string
            )

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
                    # If your children need a context, override in child streams.
                    child.sync(
                        state=state,
                        transformer=transformer,
                        parent_obj=record,
                    )

        LOGGER.info("FINISHED Syncing: %s, total_records: %d",
                    self.tap_stream_id, written)
        return written
