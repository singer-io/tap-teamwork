"""
Main entrypoint for the tap-teamwork Singer tap.
Handles discovery and sync operations.
"""

import sys
import json
import singer
from tap_teamwork.client import Client
from tap_teamwork.discover import discover
from tap_teamwork.sync import sync

LOGGER = singer.get_logger()
REQUIRED_CONFIG_KEYS = ["access_token", "start_date"]


def do_discover():
    """
    Discover and emit the catalog to stdout.
    """
    LOGGER.info("Starting discover")
    catalog = discover()
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    LOGGER.info("Finished discover")


@singer.utils.handle_top_exception(LOGGER)
def main():
    """
    Parse command-line arguments and run discovery or sync mode.
    """
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    state = parsed_args.state or {}

    with Client(parsed_args.config) as client:
        if parsed_args.discover:
            do_discover()
        elif parsed_args.catalog:
            sync(
                client,
                parsed_args.config,
                parsed_args.catalog,
                state
            )


if __name__ == "__main__":
    main()
