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
    """Raises the associated response exception.

    Takes in a response object, checks the status code,
    and throws the associated exception based on the status code.

    :param response: requests.Response object
    """
    try:
        response_json = response.json()
    except Exception:
        response_json = {}

    if response.status_code not in [200, 201, 204]:
        if response_json.get("error"):
            message = f"HTTP-error-code: {response.status_code}, Error: {response_json.get('error')}"
        else:
            message = (
                f"HTTP-error-code: {response.status_code}, Error: "
                f"{response_json.get('message', ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get('message', 'Unknown Error'))}"
            )
        exc = ERROR_CODE_EXCEPTION_MAPPING.get(response.status_code, {}).get(
            "raise_exception", teamworkError
        )
        raise exc(message, response) from None


class Client:
    """
    A wrapper class for Teamwork API requests.

    Performs:
     - Authentication
     - Response parsing
     - HTTP error handling and retries
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        self._session = session()

        site_name = config.get("site_name")
        base_url = config.get("base_url")

        if not base_url:
            if not site_name:
                raise ValueError("Missing required config property: either 'base_url' or 'site_name'")
            base_url = f"https://{site_name}.teamwork.com/"
        self.base_url = base_url.rstrip("/") + "/"

        config_request_timeout = config.get("request_timeout")
        self.request_timeout = float(config_request_timeout) if config_request_timeout else REQUEST_TIMEOUT

    def __enter__(self):
        self.check_api_credentials()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._session.close()

    def check_api_credentials(self) -> None:
        """Optionally verify API credentials before making requests."""
        pass

    def authenticate(self, headers: Dict, params: Dict) -> Tuple[Dict, Dict]:
        """Authenticates the request with the Bearer token."""
        headers["Authorization"] = f"Bearer {self.config['access_token']}"
        headers["Content-Type"] = "application/json"
        return headers, params

    def get(self, endpoint: str, params: Dict, headers: Dict, path: str = None) -> Any:
        """Calls the make_request method with a prefixed method type `GET`."""
        endpoint = endpoint or f"{self.base_url}{path}"
        headers, params = self.authenticate(headers, params)
        return self.__make_request("GET", endpoint, headers=headers, params=params, timeout=self.request_timeout)

    def post(self, endpoint: str, params: Dict, headers: Dict, body: Dict, path: str = None) -> Any:
        """Calls the make_request method with a prefixed method type `POST`."""
        try:
            endpoint = endpoint or f"{self.base_url}{path}"
            headers, params = self.authenticate(headers, params)
            # Return the dict directly to avoid the error in unit tests
            return self.__make_request(
                "POST", endpoint, headers=headers, params=params, data=body, timeout=self.request_timeout
            )
        except Exception as e:
            LOGGER.exception(f"[post] Failed POST request to {endpoint}: {e}")
            raise

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(
            ConnectionResetError,
            ConnectionError,
            ChunkedEncodingError,
            Timeout,
            teamworkBackoffError,
        ),
        max_tries=5,
        factor=2,
    )
    def __make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Mapping[Any, Any]]:
        """
        Performs HTTP operations.

        Args:
            method (str): HTTP method type (GET, POST, etc.).
            endpoint (str): URL of the resource that needs to be fetched.
            params (dict): A mapping for URL params (e.g., ?name=Avery&age=3).
            headers (dict): A mapping for the headers that need to be sent.
            data (dict): Only applicable to POST requests, body of the request.

        Returns:
            Dict, List, or None: Returns a JSON-parsed HTTP response or None if exception.
        """
        with metrics.http_request_timer(endpoint):
            response = self._session.request(method, endpoint, **kwargs)
            raise_for_error(response)

        return response.json()
