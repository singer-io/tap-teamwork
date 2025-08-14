"""Sync logic for tap-teamwork: selection, schema writing, and record syncing."""

from typing import Any, Dict, List, MutableMapping, Optional, Type
import singer

from tap_teamwork.client import Client
from tap_teamwork.streams import STREAMS

LOGGER = singer.get_logger()


def _build_stream_map() -> Dict[str, Type[Any]]:
    """
    Build a robust tap_stream_id -> class map from STREAMS.
    Supports dict, list of classes, or list of (id, class) tuples.
    """
    mapping: Dict[str, Type[Any]] = {}

    if isinstance(STREAMS, dict):
        for k, v in STREAMS.items():
            if isinstance(k, str) and isinstance(v, type):
                mapping[k] = v
        return mapping

    for item in STREAMS:
        if (
            isinstance(item, tuple)
            and len(item) == 2
            and isinstance(item[0], str)
            and isinstance(item[1], type)
        ):
            mapping[item[0]] = item[1]
            continue

        if isinstance(item, type):
            tsid = getattr(item, "tap_stream_id", None)
            if isinstance(tsid, str) and tsid:
                mapping[tsid] = item
                continue
            try:
                inst = item()
                tsid = getattr(inst, "tap_stream_id", None)
                if isinstance(tsid, str) and tsid:
                    mapping[tsid] = item
            except Exception:  # pylint: disable=broad-except
                pass

    return mapping


def _instantiate_stream(cls: Type[Any], client: Client, cat_stream: Any) -> Any:
    """
    Prefer signature (client, catalog_stream); fallback to no-arg + attach attrs.
    """
    try:
        return cls(client, cat_stream)
    except TypeError:
        inst = cls()
        if hasattr(inst, "configure") and callable(getattr(inst, "configure")):
            inst.configure(client, cat_stream)
        else:
            setattr(inst, "client", client)
            setattr(inst, "catalog_stream", cat_stream)
        return inst


def _is_child_stream(stream_obj: Any) -> bool:
    """Return True if stream has a meaningful parent reference."""
    parent_type = getattr(stream_obj, "parent_stream_type", None)
    if parent_type:
        return True
    parent_id = getattr(stream_obj, "parent", None)
    if isinstance(parent_id, str) and parent_id.strip():
        return True
    return False


def update_currently_syncing(
    state: MutableMapping[str, Any],
    stream_name: Optional[str],
) -> None:
    """Update currently_syncing in state and write it."""
    if not stream_name and singer.get_currently_syncing(state):
        state.pop("currently_syncing", None)
    else:
        singer.set_currently_syncing(state, stream_name)
    singer.write_state(state)


def write_schema(
    stream: Any,
    client: Client,
    streams_to_sync: List[str],
    catalog: singer.Catalog,
    stream_map: Dict[str, Type[Any]],
) -> None:
    """Write schema for stream and its declared children."""
    if getattr(stream, "is_selected", lambda: False)():
        stream.write_schema()

    for child_id in getattr(stream, "children", []):
        child_cls = stream_map.get(child_id)
        if not child_cls:
            LOGGER.warning("Child stream class not found for: %s", child_id)
            continue

        try:
            child_obj = _instantiate_stream(
                child_cls,
                client,
                catalog.get_stream(child_id),
            )
            write_schema(
                child_obj,
                client,
                streams_to_sync,
                catalog,
                stream_map,
            )

            if child_id in streams_to_sync and hasattr(stream, "child_to_sync"):
                stream.child_to_sync.append(child_obj)

        except (AttributeError, KeyError, ValueError) as child_err:
            LOGGER.exception(
                "Error processing child stream '%s': %s",
                child_id,
                child_err,
            )


def sync(
    client: Client,
    _config: Dict[str, Any],
    catalog: singer.Catalog,
    state: MutableMapping[str, Any],
) -> None:
    """Sync selected streams from catalog."""
    try:
        stream_map = _build_stream_map()

        streams_to_sync = [s.stream for s in catalog.get_selected_streams(state)]
        LOGGER.info("Selected streams: %s", streams_to_sync)

        last_stream = singer.get_currently_syncing(state)
        LOGGER.info("Last/currently syncing stream: %s", last_stream)

        with singer.Transformer() as transformer:
            for stream_name in streams_to_sync:
                stream_cls = stream_map.get(stream_name)
                if not stream_cls:
                    raise ValueError(
                        f"Stream class not found for: {stream_name}"
                    )

                stream = _instantiate_stream(
                    stream_cls,
                    client,
                    catalog.get_stream(stream_name),
                )

                if _is_child_stream(stream):
                    LOGGER.info("Skipping child stream: %s", stream_name)
                    continue

                write_schema(
                    stream,
                    client,
                    streams_to_sync,
                    catalog,
                    stream_map,
                )

                LOGGER.info("START Syncing: %s", stream_name)
                update_currently_syncing(state, stream_name)

                try:
                    total_records = stream.sync(
                        state=state,
                        transformer=transformer,
                    )
                except (RuntimeError, AttributeError, ValueError) as sync_err:
                    LOGGER.exception(
                        "Failed syncing stream '%s': %s",
                        stream_name,
                        sync_err,
                    )
                    update_currently_syncing(state, None)
                    continue

                update_currently_syncing(state, None)
                LOGGER.info(
                    "FINISHED Syncing: %s, total_records: %s",
                    stream_name,
                    total_records,
                )

    except (KeyError, AttributeError, ValueError) as top_err:
        LOGGER.exception("Unexpected failure in sync(): %s", top_err)
