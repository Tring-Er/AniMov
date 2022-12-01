from sys import exit

from httpx import Client, Response

DEFAULT_HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/80.0.3987.163 "
    "Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.5",
}


class HttpClient:

    def __init__(self):
        self.session = Client(timeout=10.0, headers=DEFAULT_HEADERS)

    def get(self, link: str) -> Response:
        try:
            response = self.session.get(link)
            self.session.headers["Referer"] = link
        except Exception as e:
            print(f"Error: {e}\n"
                  f"Please open an issue if this is not due due to your internet connection")
            exit(-1)
        return response

    def post(self, link: str, query: dict) -> Response:
        try:
            response = self.session.post(link, data=query)
            self.session.headers["Referer"] = link
        except Exception as e:
            print(f"Error: {e}\n"
                  f"Please open an issue if this is not due due to your internet connection")
            exit(-1)
        return response

    def set_headers(self, header: dict) -> None:
        self.session.headers = header
