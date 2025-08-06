"""Sync logic for tap-teamwork. Handles stream selection, schema writing, and record syncing."""

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


def write_schema(stream, client: Client, streams_to_sync, catalog) -> None:
    """Write schema for stream and its children."""
    if stream.is_selected():
        stream.write_schema()

    for child in stream.children:
        # Find child class from STREAMS list
        child_cls = next(
            (s for s in STREAMS if s().tap_stream_id == child), None
        )
        if not child_cls:
            LOGGER.warning(
                "[write_schema] Child stream class not found for: %s", child
            )
            continue

        try:
            child_obj = child_cls(client, catalog.get_stream(child))
            write_schema(child_obj, client, streams_to_sync, catalog)

            if child in streams_to_sync:
                stream.child_to_sync.append(child_obj)

        except (AttributeError, KeyError, ValueError) as child_err:
            LOGGER.exception(
                "[write_schema] Error processing child stream '%s': %s",
                child,
                child_err
            )


def sync(client: Client, _config: Dict, catalog: singer.Catalog, state) -> None:
    """Sync selected streams from catalog."""
    try:
        streams_to_sync = [s.stream for s in catalog.get_selected_streams(state)]
        LOGGER.info("[sync] Selected streams: %s", streams_to_sync)

        last_stream = singer.get_currently_syncing(state)
        LOGGER.info("[sync] Last/currently syncing stream: %s", last_stream)

        with singer.Transformer() as transformer:
            for stream_name in streams_to_sync:
                # Find stream class by tap_stream_id
                stream_cls = next(
                    (s for s in STREAMS if s().tap_stream_id == stream_name), None
                )
                if not stream_cls:
                    raise ValueError(
                        f"[sync] Stream class not found for: {stream_name}"
                    )

                stream = stream_cls(client, catalog.get_stream(stream_name))

                # Skip syncing child streams directly
                if hasattr(stream, "parent_stream_type"):
                    LOGGER.info("[sync] Skipping child stream: %s", stream_name)
                    continue

                write_schema(stream, client, streams_to_sync, catalog)

                LOGGER.info("[sync] START Syncing: %s", stream_name)
                update_currently_syncing(state, stream_name)

                try:
                    total_records = stream.sync(
                        state=state,
                        transformer=transformer
                    )
                except (RuntimeError, AttributeError, ValueError) as sync_err:
                    LOGGER.exception(
                        "[sync] Failed syncing stream '%s': %s",
                        stream_name,
                        sync_err
                    )
                    update_currently_syncing(state, None)
                    continue

                update_currently_syncing(state, None)
                LOGGER.info(
                    "[sync] FINISHED Syncing: %s, total_records: %s",
                    stream_name,
                    total_records
                )

    except (KeyError, AttributeError, ValueError) as top_err:
        LOGGER.exception("[sync] Unexpected failure in sync(): %s", top_err)
