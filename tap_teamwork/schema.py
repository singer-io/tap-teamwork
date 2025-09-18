"""Schema loading and metadata preparation for tap-teamwork."""

import os
import json
from typing import Dict, Tuple

import singer
from singer import metadata
from tap_teamwork.streams import STREAMS

LOGGER = singer.get_logger()


def get_abs_path(path: str) -> str:
    """
    Get the absolute path for the schema files.
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schema_references() -> Dict:
    """
    Load the schema files from the shared schema folder and return the schema references.
    """
    shared_schema_path = get_abs_path("schemas/shared")

    shared_file_names = []
    if os.path.exists(shared_schema_path):
        shared_file_names = [
            f
            for f in os.listdir(shared_schema_path)
            if os.path.isfile(os.path.join(shared_schema_path, f))
        ]

    refs = {}
    for shared_schema_file in shared_file_names:
        with open(
            os.path.join(shared_schema_path, shared_schema_file), encoding="utf-8"
        ) as data_file:
            refs[f"shared/{shared_schema_file}"] = json.load(data_file)

    return refs


def get_schemas() -> Tuple[Dict, Dict]:
    """
    Load the schema references, prepare metadata for each stream,
    and return schema and metadata for the catalog.
    """
    schemas: Dict = {}
    field_metadata: Dict = {}
    refs = load_schema_references()

    for stream_cls in STREAMS.values():
        stream_obj = stream_cls()
        stream_name = stream_obj.tap_stream_id

        schema_path = get_abs_path(f"schemas/{stream_name}.json")
        if not os.path.exists(schema_path):
            LOGGER.warning("Schema file not found: %s", schema_path)
            continue

        with open(schema_path, encoding="utf-8") as file:
            schema = json.load(file)

        schemas[stream_name] = schema
        schema = singer.resolve_schema_references(schema, refs)

        stream_metadata = metadata.get_standard_metadata(
            schema=schema,
            key_properties=getattr(stream_obj, "key_properties"),
            valid_replication_keys=(getattr(stream_obj, "replication_keys") or []),
            replication_method=getattr(stream_obj, "replication_method"),
        )
        stream_metadata = metadata.to_map(stream_metadata)

        automatic_keys = getattr(stream_obj, "replication_keys") or []
        for field_name in schema.get("properties", {}).keys():
            if field_name in automatic_keys:
                stream_metadata = metadata.write(
                    stream_metadata, ("properties", field_name), "inclusion", "automatic"
                )

        parent_tap_stream_id = getattr(stream_obj, "parent", None)
        if parent_tap_stream_id:
            stream_metadata = metadata.write(stream_metadata, (), 'parent-tap-stream-id', parent_tap_stream_id)

        field_metadata[stream_name] = metadata.to_list(stream_metadata)

    return schemas, field_metadata
