import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

class HttpClient:
    """A lightweight HTTP client with session reuse, retries, rate‑limiting and default headers.

    Parameters
    ----------
    email: str | None
        Optional email to include in the ``From`` header – useful for NCBI APIs.
    max_retries: int, default 3
        Number of total retry attempts for transient failures.
    backoff_factor: float, default 0.5
        Factor for exponential back‑off (seconds) used by ``urllib3.Retry``.
    status_forcelist: tuple[int], default (429, 500, 502, 503, 504)
        HTTP status codes that should trigger a retry.
    """

    def __init__(self, email: str | None = None, max_retries: int = 3,
                 backoff_factor: float = 0.5,
                 status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504)):
        self.session = requests.Session()
        # Default headers – mimic a browser to avoid simple blocks.
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; LeadLattice/1.0; +https://leadlattice.ai)",
            "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
        })
        if email:
            self.session.headers["From"] = email

        # Configure retry strategy.
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _rate_limit_delay(self) -> None:
        """Sleep a short random interval before each request to avoid hammering the target."""
        time.sleep(random.uniform(0.5, 1.5))

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        self._rate_limit_delay()
        response = self.session.request(method=method.upper(), url=url, **kwargs)
        return response

    def get(self, url: str, **kwargs) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        return self.request("POST", url, **kwargs)
