"""Sync logic for tap-teamwork: selection, schema writing, and record syncing."""

from typing import Dict

import singer

from tap_teamwork.client import Client
from tap_teamwork.streams import STREAMS

LOGGER = singer.get_logger()


def update_currently_syncing(state: Dict, stream_name: str) -> None:
    """Update currently_syncing in state and write it."""
    if not stream_name and singer.get_currently_syncing(state):
        del state["currently_syncing"]
    else:
        singer.set_currently_syncing(state, stream_name)
    singer.write_state(state)


def _instantiate_stream(cls, client: Client, cat_stream) -> object:
    """
    Prefer standard (client, catalog_stream); gracefully fallback to no-arg.

    This keeps compatibility with streams that were generated with a no-arg
    constructor and expect configure()/attribute injection.
    """
    try:
        return cls(client, cat_stream)
    except TypeError:
        inst = cls()
        cfg = getattr(inst, "configure", None)
        if callable(cfg):
            cfg(client, cat_stream)
            return inst
        # last-resort attribute injection
        setattr(inst, "client", client)
        setattr(inst, "catalog_stream", cat_stream)
        return inst


def write_schema(stream, client, streams_to_sync, catalog) -> None:
    """Write schema for stream and its children."""
    if getattr(stream, "is_selected", lambda: False)():
        stream.write_schema()

    for child in getattr(stream, "children", []) or []:
        child_obj = _instantiate_stream(
            STREAMS[child],
            client,
            catalog.get_stream(child),
        )
        write_schema(child_obj, client, streams_to_sync, catalog)
        if child in streams_to_sync:
            stream.child_to_sync.append(child_obj)


def sync(  # pylint: disable=unused-argument
    client: Client,
    config: Dict,
    catalog: singer.Catalog,
    state,
) -> None:
    """Sync selected streams from catalog."""
    streams_to_sync = [s.stream for s in catalog.get_selected_streams(state)]
    LOGGER.info("selected_streams: %s", streams_to_sync)

    last_stream = singer.get_currently_syncing(state)
    LOGGER.info("last/currently syncing stream: %s", last_stream)

    with singer.Transformer() as transformer:
        for stream_name in streams_to_sync:
            stream = _instantiate_stream(
                STREAMS[stream_name],
                client,
                catalog.get_stream(stream_name),
            )

            # If this is a child and its parent isn't selected, schedule the parent.
            if getattr(stream, "parent", None):
                if stream.parent not in streams_to_sync:
                    streams_to_sync.append(stream.parent)
                continue

            write_schema(stream, client, streams_to_sync, catalog)

            LOGGER.info("START Syncing: %s", stream_name)
            update_currently_syncing(state, stream_name)

            # Support both return shapes: count OR (count, state).
            result = stream.sync(state=state, transformer=transformer)
            try:
                total_records, state = result  # some taps return (count, state)
            except (TypeError, ValueError):
                total_records = result  # others return just count

            update_currently_syncing(state, None)
            LOGGER.info(
                "FINISHED Syncing: %s, total_records: %s",
                stream_name,
                total_records,
            )
