from typing import Any, Dict, Mapping, Optional, Tuple

import backoff
import requests
from requests import session
from requests.exceptions import Timeout, ConnectionError, ChunkedEncodingError
from singer import get_logger, metrics

from tap_teamwork.exceptions import ERROR_CODE_EXCEPTION_MAPPING, teamworkError, teamworkBackoffError

LOGGER = get_logger()
REQUEST_TIMEOUT = 300

def raise_for_error(response: requests.Response) -> None:
    """
    Raises the associated response exception based on status code and body.
    Only raises if the status code is not in the success list (200, 201, 204).
    """
    try:
        response_json = response.json()
    except Exception as e:
        LOGGER.warning(f"[raise_for_error] Failed to parse response JSON: {e}")
        response_json = {}

    if response.status_code not in [200, 201, 204]:
        if response_json.get("error"):
            message = f"HTTP-error-code: {response.status_code}, Error: {response_json.get('error')}"
        else:
            message = f"HTTP-error-code: {response.status_code}, Error: {response_json.get('message', ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get('message', 'Unknown Error'))}"
        exc = ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get("raise_exception", teamworkError)
        LOGGER.error(f"[raise_for_error] Raising exception for status {response.status_code}: {message}")
        raise exc(message, response) from None

class Client:
    """
    HTTP Client for Teamwork API with:
    - Token-based authentication
    - GET/POST support
    - Error handling
    - Retry with exponential backoff
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        self._session = session()
        self.base_url = config.get("base_url", "https://qlik6.teamwork.com/")
        config_request_timeout = config.get("request_timeout")
        self.request_timeout = float(config_request_timeout) if config_request_timeout else REQUEST_TIMEOUT

    def __enter__(self):
        self.check_api_credentials()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._session.close()

    def check_api_credentials(self) -> None:
        """Placeholder for optional auth check."""
        pass

    def authenticate(self, headers: Dict, params: Dict) -> Tuple[Dict, Dict]:
        """Adds authentication headers to the request."""
        try:
            headers["Authorization"] = f"Bearer {self.config['access_token']}"
            headers["Content-Type"] = "application/json"
        except KeyError as e:
            LOGGER.exception("[authenticate] Missing access_token in config")
            raise teamworkError("Missing required access_token in config") from e
        return headers, params

    def get(self, endpoint: str, params: Dict, headers: Dict, path: str = None) -> Any:
        """Performs a GET request."""
        try:
            endpoint = endpoint or f"{self.base_url}/{path}"
            headers, params = self.authenticate(headers, params)
            return self.__make_request("GET", endpoint, headers=headers, params=params, timeout=self.request_timeout)
        except Exception as e:
            LOGGER.exception(f"[get] Failed GET request to {endpoint}: {e}")
            raise

    def post(self, endpoint: str, params: Dict, headers: Dict, body: Dict, path: str = None) -> Any:
        """Performs a POST request."""
        try:
            endpoint = endpoint or f"{self.base_url}/{path}"
            headers, params = self.authenticate(headers, params)
            return self.__make_request(
                "POST",
                endpoint,
                headers=headers,
                params=params,
                json=body,
                timeout=self.request_timeout
            )
        except Exception as e:
            LOGGER.exception(f"[post] Failed POST request to {endpoint}: {e}")
            raise

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(ConnectionResetError, ConnectionError, ChunkedEncodingError, Timeout, teamworkBackoffError),
        max_tries=5,
        factor=2,
    )
    def __make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Mapping[Any, Any]]:
        """
        Makes the HTTP request and raises errors as needed.
        """
        try:
            with metrics.http_request_timer(endpoint):
                response = self._session.request(method, endpoint, **kwargs)
                raise_for_error(response)
                return response.json()
        except Exception as e:
            LOGGER.exception(f"[__make_request] {method} request to {endpoint} failed: {e}")
            raise
