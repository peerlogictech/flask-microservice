import logging
import requests
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

class InvalidBaseCurrencyException(Exception):
    pass


class RateLimited(Exception):
    pass


class ImproperConfiguration(Exception):
    pass

class NotFound(Exception):
    pass

class FreeCurrencyAPIClient(object):
    def __init__(self, base_url: str, api_key: str = None) -> None:
        super().__init__()
        if not base_url:
            raise ImproperConfiguration(
                "No base url configured for FreeCurrencyAPIClient"
            )
        self._base_url = base_url
        self._session = requests.Session()
        self._session.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            # Header for apikey doesn't work
        }
        if api_key:
            self._session.params = {"apikey": api_key}

    def get_rates(self, from_currency: str) -> requests.Response:
        self._session.params["base_currency"] = from_currency
        try:
            response = self._session.get(f"{self._base_url}/rates")
            if response.status_code == 500:
                # Unfortunately when you give a bad base_currency it gives a 500 instead of 400
                # TODO: use a more reliable rest api due to this issue
                raise InvalidBaseCurrencyException(
                    "Error: Possible invalid base_currency"
                )
            if response.status_code == 429:
                raise RateLimited(
                    "Slow down, this service is free and it needs you to be gentle!"
                )

            if response.status_code == 404:
                raise NotFound(f"No exchange currencies found for {from_currency}")

            response.raise_for_status()

        except (requests.ConnectionError, requests.Timeout) as e:
            print(str(e))
            raise Exception("We're sorry, we're experiencing degraded service.")

        return response
