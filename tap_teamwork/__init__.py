"""
Main entry point for the tap-teamwork Singer tap.

Handles discovery (--discover) and sync (with a provided catalog).
"""

import json
import sys
from typing import Any, Dict

import singer
from tap_teamwork.client import Client
from tap_teamwork.discover import discover
from tap_teamwork.sync import sync

LOGGER = singer.get_logger()

# We still allow an advanced 'base_url' override in client.py, but
# 'subdomain' must be provided in config for standard usage.
REQUIRED_CONFIG_KEYS = ["access_token", "start_date", "subdomain"]


def do_discover() -> None:
    """Discover and emit the catalog to stdout."""
    LOGGER.info("Starting discover")
    catalog = discover()
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    LOGGER.info("Finished discover")


@singer.utils.handle_top_exception(LOGGER)
def main() -> None:
    """Parse command-line arguments and run discovery or sync mode."""
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    state: Dict[str, Any] = parsed_args.state or {}

    # Build client (validates subdomain/base_url and normalizes base_url)
    with Client(parsed_args.config) as client:
        if parsed_args.discover:
            do_discover()
            return

        if parsed_args.catalog:
            # Call sync POSITIONALLY to avoid name-mismatch (_config vs config)
            sync(client, parsed_args.config, parsed_args.catalog, state)
            return

        raise SystemExit("No mode specified: use --discover or provide a catalog for sync.")


if __name__ == "__main__":
    main()
