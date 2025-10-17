"""HTTP client for Teamwork API with auth, retries, and error handling."""

from typing import Any, Dict, Mapping, Optional, Tuple
import json

import backoff, time
import requests
from requests import session
from requests.exceptions import (
    Timeout,
    ConnectionError as RequestsConnectionError,
    ChunkedEncodingError,
)
from singer import get_logger, metrics

from tap_teamwork.exceptions import (
    ERROR_CODE_EXCEPTION_MAPPING,
    teamworkError,
    teamworkBackoffError,
)

LOGGER = get_logger()
REQUEST_TIMEOUT = 300


def raise_for_error(response: requests.Response) -> None:
    """Raise a domain-specific exception for non-2xx responses."""
    try:
        response_json = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        LOGGER.warning("Failed to parse response JSON: %s", exc)
        response_json = {}

    if response.status_code in (200, 201, 204):
        return

    payload_msg = response_json.get("error") or response_json.get("message")
    mapped_msg = ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get(
        "message", "Unknown Error"
    )
    message = f"HTTP {response.status_code}: {payload_msg or mapped_msg}"

    exc_class = ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get(
        "raise_exception", teamworkError
    )
    LOGGER.error("Raising exception for status %s: %s", response.status_code, message)
    raise exc_class(message, response) from None

def wait_if_retry_after(details):
    """Backoff handler that checks for a 'retry_after' attribute in the exception
    and sleeps for the specified duration to respect API rate limits.
    """
    exc = details['exception']
    if hasattr(exc, 'retry_after') and exc.retry_after is not None:
        time.sleep(exc.retry_after)  # Force exact wait

class Client:
    """
    HTTP Client wrapper that handles:
      - Authentication (Bearer token)
      - Response parsing and metrics
      - HTTP error handling + retry
      - Dynamic Teamwork base URL from config (built from subdomain only)
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config: Dict[str, Any] = dict(config)
        self._session = session()

        # Build base URL from subdomain and normalize: NO trailing slash
        self.base_url = self._build_base_url_from_subdomain().rstrip("/")

        # Request timeout
        config_request_timeout = self.config.get("request_timeout")
        self.request_timeout = (
            float(config_request_timeout) if config_request_timeout else REQUEST_TIMEOUT
        )

    def _build_base_url_from_subdomain(self) -> str:
        subdomain = self.config.get("subdomain")
        if not subdomain:
            raise ValueError("Missing required config property: 'subdomain'.")
        return f"https://{subdomain}.teamwork.com/"

    def __enter__(self):
        self.check_api_credentials()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._session.close()

    def check_api_credentials(self) -> None:
        """Optional pre-flight check (no-op placeholder)."""
        return

    def authenticate(self, headers: Dict, params: Dict) -> Tuple[Dict, Dict]:
        """Attach Bearer token & JSON headers; raise if token missing."""
        try:
            headers["Authorization"] = f"Bearer {self.config['access_token']}"
            headers["Content-Type"] = "application/json"
        except KeyError as exc:
            LOGGER.exception("Missing access_token in config")
            raise teamworkError("Missing required access_token in config") from exc
        return headers, params

    # ---------- Single source of truth for URL building ----------
    def build_url(self, path: str) -> str:
        """Join base_url and relative path with normalized single slash."""
        return f"{self.base_url}/{(path or '').lstrip('/')}"

    def _resolve_endpoint(self, endpoint: Optional[str], path: Optional[str]) -> str:
        """
        If an absolute endpoint is provided, return it.
        Otherwise, build from base_url + path (normalized).
        """
        if endpoint:
            return endpoint
        return self.build_url(path or "")

    def get(self, endpoint: str, params: Dict, headers: Dict, path: str = None) -> Any:
        """Perform a GET request."""
        try:
            final_url = self._resolve_endpoint(endpoint, path)
            headers, params = self.authenticate(headers, params)
            LOGGER.info("Final URL: %s", final_url)
            return self.__make_request(
                "GET",
                final_url,
                headers=headers,
                params=params,
                timeout=self.request_timeout,
            )
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.exception("Failed GET request to %s: %s", endpoint or path, exc)
            raise

    def post(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        endpoint: str,
        params: Dict,
        headers: Dict,
        body: Dict,
        path: str = None,
    ) -> Any:
        """Perform a POST request."""
        try:
            final_url = self._resolve_endpoint(endpoint, path)
            headers, params = self.authenticate(headers, params)
            LOGGER.info("Final URL: %s", final_url)
            return self.__make_request(
                "POST",
                final_url,
                headers=headers,
                params=params,
                json=body,
                timeout=self.request_timeout,
            )
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.exception("Failed POST request to %s: %s", endpoint or path, exc)
            raise

    @backoff.on_exception(
        wait_gen=lambda: backoff.expo(factor=2),
        on_backoff=wait_if_retry_after,
        exception=(
            ConnectionResetError,
            RequestsConnectionError,
            ChunkedEncodingError,
            Timeout,
            teamworkBackoffError,
        ),
        max_tries=5,
    )
    def __make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Optional[Mapping[str, Any]]:
        """Low-level HTTP request/response handler with metrics + error raising."""
        try:
            with metrics.http_request_timer(endpoint):
                response = self._session.request(method, endpoint, **kwargs)
                raise_for_error(response)
                return response.json()
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.exception("%s request to %s failed: %s", method, endpoint, exc)
            raise
