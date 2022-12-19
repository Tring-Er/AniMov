import json

from httpx import Response

from animov.use_cases.streaming_providers.Provider import Provider
from animov.elements.Media import Media
from animov.interfaces.Downloaders.MediaDownloader import MediaDownloader
from animov.interfaces.Players.MediaPlayer import MediaPlayer
from animov.elements.HtmlParser import HtmlParser
from animov.elements.HttpClient import HttpClient


class TheFlix(Provider):
    BASE_URL = "https://theflix.to"
    COOKIES_URL = "https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing"
    COOKIES_QUERY = {"affiliateCode": "", "pathname": "/"}
    BASE_MOVIE_CDN_URL = "https://theflix.to:5679/movies/videos/{}/request-access?contentUsageType=Viewing"
    BASE_TV_SHOW_EPISODE_CDN_URL = "https://theflix.to:5679/tv/videos/{}/request-access?contentUsageType=Viewing"

    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client
        self.create_cookies()

    def create_cookies(self) -> None:
        response = self.http_client.post_request(self.COOKIES_URL, self.COOKIES_QUERY)
        cookie = response.headers["Set-Cookie"]
        self.http_client.set_headers({"Cookie": cookie})

    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        return f"{self.BASE_URL}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}"

    def create_movie_url(self, show_title: str, show_id: int) -> str:
        return f"{self.BASE_URL}/movie/{show_id}-{show_title}"

    def filter_episode_cdn_data(self, show_data: str, selected_season: str, selected_episode: str) -> str | Exception:
        try:
            episode_id = json.loads(HtmlParser(show_data, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"][int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except Exception as error:
            return error
        return episode_id

    def filter_episode_cdn_url_response(self, response_data: Response) -> str:
        return response_data.json()["url"]

    def download_or_play_tv_show(self, show: Media, selected_season: str, selected_episode: str, mode: str) -> None | str | Exception:
        url = self.get_tv_show_url(show.title, show.show_id, selected_season, selected_episode)
        episode_cdn_id_data = self.http_client.get_request(url).text
        episode_cdn_id_or_exception = self.filter_episode_cdn_data(episode_cdn_id_data, selected_season, selected_episode)
        if isinstance(episode_cdn_id_or_exception, Exception):
            return episode_cdn_id_or_exception
        episode_cdn_url_data = self.http_client.get_request(self.BASE_TV_SHOW_EPISODE_CDN_URL.format(episode_cdn_id_or_exception))
        episode_cdn_url = self.filter_episode_cdn_url_response(episode_cdn_url_data)
        if mode == "d":
            download_path = MediaDownloader.download_show(episode_cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(episode_cdn_url, show.title, self.BASE_URL)
            if isinstance(error, Exception):
                return error

    def filter_show_cdn_id(self, response_data: str) -> str:
        show_cdn_id: str = json.loads(HtmlParser(response_data, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        return show_cdn_id

    def filter_cdn_data(self, response_data: Response) -> str:
        return response_data.json()["url"]

    def download_or_play_movie(self, show: Media, mode: str) -> None | str | Exception:
        show_url = self.create_movie_url(show.title, show.show_id)
        show_cdn_data = self.http_client.get_request(show_url).text
        show_cdn_id = self.filter_show_cdn_id(show_cdn_data)
        cdn_data = self.http_client.get_request(self.BASE_MOVIE_CDN_URL.format(show_cdn_id))
        cdn_url = self.filter_cdn_data(cdn_data)
        if mode == "d":
            download_path = MediaDownloader.download_show(cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url, show.title, self.BASE_URL)
            return error
