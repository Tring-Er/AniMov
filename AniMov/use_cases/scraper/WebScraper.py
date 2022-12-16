import json

from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.HtmlParser import HtmlParser
from AniMov.elements.Media import Media
from AniMov.use_cases.streaming_providers.Provider import Provider
from AniMov.interfaces.Downloaders.MediaDownloader import MediaDownloader
from AniMov.interfaces.Players.MediaPlayer import MediaPlayer


class WebScraper:

    def __init__(self, http_client: HttpClient, provider: Provider) -> None:
        self.http_client = http_client
        self.provider = provider
        self.cookies = self.create_cookies(self.provider.COOKIES_URL, self.provider.COOKIES_QUERY)

    def create_cookies(self, url: str, url_query: dict) -> str:
        response = self.http_client.post_request(url, url_query)
        return response.headers["Set-Cookie"]

    def get_movie_cdn_id(self, show_url: str, cookies: str) -> str:
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_id: str = json.loads(HtmlParser(self.http_client.get_request(show_url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        return show_cdn_id

    def get_movie_cnd_url(self, base_cdn_url: str, show_cdn_id: str, cookies: str) -> str:
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_url: str = self.http_client.get_request(base_cdn_url.format(show_cdn_id)).json()["url"]
        return show_cdn_url

    def get_episode_cdn_id(self, url: str, selected_season: str, selected_episode: str, cookies: str) -> str | Exception:
        self.http_client.set_headers({"Cookie": cookies})
        show_data = json.loads(HtmlParser(self.http_client.get_request(url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = show_data[int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except Exception as error:
            return error
        return episode_id

    def get_episode_cdn_url(self, episode_base_cdn_url: str, episode_id: str, cookies: str) -> str:
        self.http_client.set_headers({"Cookie": cookies})
        cdn_url = self.http_client.get_request(episode_base_cdn_url.format(episode_id)).json()["url"]
        return cdn_url

    def download_or_play_movie(self, show: Media, mode: str) -> None | str | Exception:
        show_url = self.provider.create_movie_url(show.title, show.show_id)
        show_cdn_id = self.get_movie_cdn_id(show_url, self.cookies)
        cdn_url = self.get_movie_cnd_url(self.provider.BASE_MOVIE_CDN_URL, show_cdn_id, self.cookies)
        if mode == "d":
            download_path = MediaDownloader.download_show(cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url, show.title, self.provider.BASE_URL)
            return error

    def download_or_play_tv_show(self, show: Media, selected_season: str, selected_episode: str, mode: str) -> None | str | Exception:
        url = self.provider.get_tv_show_url(show.title, show.show_id, selected_season, selected_episode)
        episode_cdn_id_or_exception = self.get_episode_cdn_id(url, selected_season, selected_episode, self.cookies)
        if isinstance(episode_cdn_id_or_exception, Exception):
            return episode_cdn_id_or_exception
        cdn_url = self.get_episode_cdn_url(self.provider.BASE_TV_SHOW_EPISODE_CDN_URL, episode_cdn_id_or_exception, self.cookies)
        if mode == "d":
            download_path = MediaDownloader.download_show(cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url, show.title, self.provider.BASE_URL)
            if isinstance(error, Exception):
                return error
