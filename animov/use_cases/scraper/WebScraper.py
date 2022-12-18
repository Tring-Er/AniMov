from httpx import Response

from animov.elements.HttpClient import HttpClient


class WebScraper:

    def __init__(self, http_client: HttpClient, cookies_url: str, cookies_query: dict) -> None:
        self.http_client = http_client
        self.cookies = self.create_cookies(cookies_url, cookies_query)

    def create_cookies(self, url: str, url_query: dict) -> str:
        response = self.http_client.post_request(url, url_query)
        return response.headers["Set-Cookie"]

    def get_movie_cdn_data(self, show_url: str) -> str:
        self.http_client.set_headers({"Cookie": self.cookies})
        response = self.http_client.get_request(show_url).text
        return response

    def get_movie_cnd_url(self, base_cdn_url: str, show_cdn_id: str) -> Response:
        self.http_client.set_headers({"Cookie": self.cookies})
        show_cdn_url = self.http_client.get_request(base_cdn_url.format(show_cdn_id))
        return show_cdn_url

    def get_episode_cdn_id(self, url: str) -> str:
        self.http_client.set_headers({"Cookie": self.cookies})
        show_data = self.http_client.get_request(url).text
        return show_data

    def get_episode_cdn_url(self, episode_base_cdn_url: str, episode_id: str) -> Response:
        self.http_client.set_headers({"Cookie": self.cookies})
        cdn_url = self.http_client.get_request(episode_base_cdn_url.format(episode_id))
        return cdn_url
