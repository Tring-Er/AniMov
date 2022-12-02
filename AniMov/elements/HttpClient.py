from httpx import Client, Response

DEFAULT_HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/80.0.3987.163 "
    "Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.5",
}


class HttpClient:
    """An interface for httpx library"""

    def __init__(self):
        self.session = Client(timeout=10.0, headers=DEFAULT_HEADERS)

    def get(self, link: str) -> Response:
        response = self.session.get(link)
        self.session.headers["Referer"] = link
        return response

    def post(self, link: str, query: dict) -> Response:
        response = self.session.post(link, data=query)
        self.session.headers["Referer"] = link
        return response

    def set_headers(self, header: dict) -> None:
        self.session.headers = header
