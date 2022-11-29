import time

from .httpclient import HttpClient


class KP:
    def __init__(self, website: str, time: int = 120):
        self.client = HttpClient()
        self.time = time
        self.website = website

    def ping(self, website: str = None, headers: dict = None):
        if not website:
            website = self.website
        while True:
            self.client.set_headers(headers)
            response = self.client.get(website)
            print(response.text)
            time.sleep(self.time)
