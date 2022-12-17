import json

from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.HtmlParser import HtmlParser


class WebScraper:

    def __init__(self, http_client: HttpClient, cookies_url: str, cookies_query: dict) -> None:
        self.http_client = http_client
        self.cookies = self.create_cookies(cookies_url, cookies_query)

    def create_cookies(self, url: str, url_query: dict) -> str:
        response = self.http_client.post_request(url, url_query)
        return response.headers["Set-Cookie"]

    def get_movie_cdn_id(self, show_url: str) -> str:
        self.http_client.set_headers({"Cookie": self.cookies})
        show_cdn_id: str = json.loads(HtmlParser(self.http_client.get_request(show_url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        return show_cdn_id

    def get_movie_cnd_url(self, base_cdn_url: str, show_cdn_id: str) -> str:
        self.http_client.set_headers({"Cookie": self.cookies})
        show_cdn_url: str = self.http_client.get_request(base_cdn_url.format(show_cdn_id)).json()["url"]
        return show_cdn_url

    def get_episode_cdn_id(self, url: str, selected_season: str, selected_episode: str) -> str | Exception:
        self.http_client.set_headers({"Cookie": self.cookies})
        show_data = json.loads(HtmlParser(self.http_client.get_request(url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = show_data[int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except Exception as error:
            return error
        return episode_id

    def get_episode_cdn_url(self, episode_base_cdn_url: str, episode_id: str) -> str:
        self.http_client.set_headers({"Cookie": self.cookies})
        cdn_url = self.http_client.get_request(episode_base_cdn_url.format(episode_id)).json()["url"]
        return cdn_url
