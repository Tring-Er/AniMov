from time import sleep

from AniMov.utils.httpclient import HttpClient


class Pinger:
    """Pings the server"""

    def __init__(self, ping_frequency: int = 120):
        self.http_client = HttpClient()
        self.ping_frequency = ping_frequency

    def ping(self, link: str, request_headers: dict = None):
        while True:
            self.http_client.set_headers(request_headers)
            self.http_client.get(link)
            sleep(self.ping_frequency)
