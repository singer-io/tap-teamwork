"""HTTP client for Teamwork API with auth, retries, and error handling."""

from typing import Any, Dict, Mapping, Optional, Tuple
import json

import backoff
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
    """
    Raise a domain-specific exception for non-2xx responses.

    Tries to parse JSON error payload; falls back to status mapping.
    """
    try:
        response_json = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        # Endpoints sometimes return non-JSON bodies (HTML, text, empty).
        LOGGER.warning("Failed to parse response JSON: %s", exc)
        response_json = {}

    if response.status_code in (200, 201, 204):
        return

    # Prefer explicit "error" key, else "message", else mapping default
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


class Client:
    """
    HTTP Client wrapper that handles:
      - Authentication (Bearer token)
      - Response parsing and metrics
      - HTTP error handling + retry
      - Dynamic Teamwork base URL from config (subdomain or base_url)
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config: Dict[str, Any] = dict(config)
        self._session = session()

        # Prefer explicit base_url; else construct from required subdomain
        base_url = self.config.get("base_url")
        subdomain = self.config.get("subdomain")
        if not base_url:
            if not subdomain:
                raise ValueError(
                    "Missing required config property: 'subdomain' "
                    "(or provide advanced override 'base_url')."
                )
            base_url = f"https://{subdomain}.teamwork.com/"

        # Normalize exactly one trailing slash
        self.base_url = base_url.rstrip("/") + "/"

        # Request timeout
        config_request_timeout = self.config.get("request_timeout")
        self.request_timeout = (
            float(config_request_timeout) if config_request_timeout else REQUEST_TIMEOUT
        )

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

    # ---------- New helper to unify endpoint construction ----------
    def _resolve_endpoint(self, endpoint: Optional[str], path: Optional[str]) -> str:
        """
        Build the absolute request URL from an explicit endpoint or a relative path.

        - If `endpoint` is provided, return it as-is.
        - Else, join `base_url` with a left-stripped `path` (or empty string).
        - If both are missing, this returns `base_url` (consistent with prior behavior).
        """
        if endpoint:
            return endpoint
        return f"{self.base_url}{(path or '').lstrip('/')}"

    def get(self, endpoint: str, params: Dict, headers: Dict, path: str = None) -> Any:
        """Perform a GET request."""
        try:
            endpoint = self._resolve_endpoint(endpoint, path)
            headers, params = self.authenticate(headers, params)
            return self.__make_request(
                "GET",
                endpoint,
                headers=headers,
                params=params,
                timeout=self.request_timeout,
            )
        except Exception as exc:  # pylint: disable=broad-except
            # Intentionally broad so callers don’t need to wrap every request.
            LOGGER.exception("Failed GET request to %s: %s", endpoint, exc)
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
            endpoint = self._resolve_endpoint(endpoint, path)
            headers, params = self.authenticate(headers, params)
            return self.__make_request(
                "POST",
                endpoint,
                headers=headers,
                params=params,
                json=body,
                timeout=self.request_timeout,
            )
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.exception("Failed POST request to %s: %s", endpoint, exc)
            raise

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(
            ConnectionResetError,
            RequestsConnectionError,
            ChunkedEncodingError,
            Timeout,
            teamworkBackoffError,
        ),
        max_tries=5,
        factor=2,
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
