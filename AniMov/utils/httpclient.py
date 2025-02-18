import sys

import httpx

DEFAULT_HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/80.0.3987.163 "
    "Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.5",
}


class HttpClient:

    def __init__(self):
        self.session = httpx.Client(timeout=10.0, headers=DEFAULT_HEADERS)

    def get(self, page: str) -> httpx.Response:
        print(page)
        try:
            response = self.session.get(page)
            self.session.headers["Referer"] = page
        except Exception as e:
            print(
                f"Error: {e}",
                "\n Please open an issue if this is not due due to your internet connection",
            )
            sys.exit(-1)
        return response

    def post(self, page: str, data: dict) -> httpx.Response:
        try:
            response = self.session.post(page, data=data)
            self.session.headers["Referer"] = page
        except Exception as e:
            print(
                f"Error: {e}",
                "\n Please open an issue if this is not due due to your internet connection",
            )
            sys.exit(-1)
        return response

    def set_headers(self, header: dict) -> None:
        self.session.headers = header

    def add_elem(self, elements: dict) -> None:
        for i in elements.items():
            self.session.headers[i[0]] = i[1]
