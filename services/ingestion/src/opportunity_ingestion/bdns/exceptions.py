class BdnsError(Exception):
    """Base exception for the exploratory BDNS client."""


class BdnsHttpError(BdnsError):
    def __init__(self, status_code: int, url: str, message: str = "") -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"BDNS HTTP {status_code} for {url}{': ' + message if message else ''}")


class BdnsInvalidJsonError(BdnsError):
    """The service returned a successful response that was not valid JSON."""


class BdnsRequestError(BdnsError):
    """A transport-level request error or exhausted retry sequence."""

