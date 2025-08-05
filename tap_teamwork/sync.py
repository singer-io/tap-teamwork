import singer
from typing import Dict
from tap_teamwork.streams import STREAMS
from tap_teamwork.client import Client

LOGGER = singer.get_logger()


def update_currently_syncing(state: Dict, stream_name: str) -> None:
    """
    Update currently_syncing in state and write it
    """
    if not stream_name and singer.get_currently_syncing(state):
        del state["currently_syncing"]
    else:
        singer.set_currently_syncing(state, stream_name)
    singer.write_state(state)


def write_schema(stream, client, streams_to_sync, catalog) -> None:
    """
    Write schema for stream and its children (works with STREAMS as a list).
    """
    if stream.is_selected():
        stream.write_schema()

    for child in stream.children:
        # Find child class from STREAMS list
        child_cls = next((s for s in STREAMS if s().tap_stream_id == child), None)
        if not child_cls:
            LOGGER.warning(f"Child stream class not found for: {child}")
            continue

        child_obj = child_cls(client, catalog.get_stream(child))
        write_schema(child_obj, client, streams_to_sync, catalog)

        if child in streams_to_sync:
            stream.child_to_sync.append(child_obj)


def sync(client: Client, config: Dict, catalog: singer.Catalog, state) -> None:
    """
    Sync selected streams from catalog
    """

    streams_to_sync = []
    for stream in catalog.get_selected_streams(state):
        streams_to_sync.append(stream.stream)
    LOGGER.info("selected_streams: {}".format(streams_to_sync))

    last_stream = singer.get_currently_syncing(state)
    LOGGER.info("last/currently syncing stream: {}".format(last_stream))

    with singer.Transformer() as transformer:
        for stream_name in streams_to_sync:
            # Find stream class by tap_stream_id
            stream_cls = next((s for s in STREAMS if s().tap_stream_id == stream_name), None)
            if not stream_cls:
                raise ValueError(f"Stream class not found for: {stream_name}")

            stream = stream_cls(client, catalog.get_stream(stream_name))

            # Skip syncing child streams directly — they will be synced via parents
            if hasattr(stream, "parent_stream_type"):
                continue

            write_schema(stream, client, streams_to_sync, catalog)

            LOGGER.info("START Syncing: {}".format(stream_name))
            update_currently_syncing(state, stream_name)
            total_records = stream.sync(state=state, transformer=transformer)
            update_currently_syncing(state, None)

            LOGGER.info(
                "FINISHED Syncing: {}, total_records: {}".format(
                    stream_name, total_records
                )
            )
