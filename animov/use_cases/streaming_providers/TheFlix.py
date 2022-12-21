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
    BASE_MEDIA_URL = BASE_URL + "/{}/{}-{}"
    BASE_MEDIA_CDN_URL = BASE_URL + ":5679/{}/videos/{}/request-access?contentUsageType=Viewing"

    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client
        self.create_cookies()

    def filter_cdn_data(self, response_data: Response) -> str:
        return response_data.json()["url"]

    def create_cookies(self) -> None:
        response = self.http_client.post_request(self.COOKIES_URL, self.COOKIES_QUERY)
        cookie = response.headers["Set-Cookie"]
        self.http_client.set_headers({"Cookie": cookie})

    def create_media_cdn_url(self, media: Media, media_cdn_id: str) -> str:
        if media.show_type == "MOVIE":
            return self.BASE_MEDIA_CDN_URL.format("movies", media_cdn_id)
        return self.BASE_MEDIA_CDN_URL.format("tv", media_cdn_id)

    def create_media_url(self, media: Media, **kwargs) -> str:
        selected_season = kwargs.get("selected_season", None)
        selected_episode = kwargs.get("selected_episode", None)
        if media.show_type == "MOVIE":
            return self.BASE_MEDIA_URL.format("movie", media.show_id, media.title)
        return self.BASE_MEDIA_URL.format("tv-show", media.show_id, media.title) + f"/season-{selected_season}/episode-{selected_episode}"

    def filter_episode_cdn_data(self, show_data: str, selected_season: str, selected_episode: str) -> str:
        try:
            episode_id = json.loads(HtmlParser(show_data, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"][int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except KeyError:
            raise KeyError(f"Episode {selected_episode} season {selected_season} it's not available.")
        return episode_id

    def get_episode_cdn_url(self, show: Media, selected_season: str, selected_episode: str) -> str:
        url = self.create_media_url(show, selected_season=selected_season, selected_episode=selected_episode)
        episode_cdn_id_data = self.http_client.get_request(url).text
        episode_cdn_id = self.filter_episode_cdn_data(episode_cdn_id_data, selected_season, selected_episode)
        episode_cdn_url_data = self.http_client.get_request(self.create_media_cdn_url(show, episode_cdn_id))
        episode_cdn_url = self.filter_cdn_data(episode_cdn_url_data)
        return episode_cdn_url

    def filter_show_cdn_id(self, response_data: str) -> str:
        return json.loads(HtmlParser(response_data, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]

    def get_movie_cdn_url(self, show: Media) -> str:
        show_url = self.create_media_url(show)
        show_cdn_data = self.http_client.get_request(show_url).text
        show_cdn_id = self.filter_show_cdn_id(show_cdn_data)
        cdn_data = self.http_client.get_request(self.create_media_cdn_url(show, show_cdn_id))
        cdn_url = self.filter_cdn_data(cdn_data)
        return cdn_url

    def get_cdn_url(self, media: Media, **kwargs) -> str:
        selected_season = kwargs.get("selected_season", None)
        selected_episode = kwargs.get("selected_episode", None)
        if media.show_type == "MOVIE":
            return self.get_movie_cdn_url(media)
        return self.get_episode_cdn_url(media, selected_season, selected_episode)

    def play_media(self, media: Media, **kwargs) -> None:
        cdn_url = self.get_cdn_url(media, **kwargs)
        MediaPlayer.play_media(cdn_url, media.title, self.BASE_URL)

    def download_media(self, media: Media, **kwargs) -> str:
        cdn_url = self.get_cdn_url(media, **kwargs)
        download_path = MediaDownloader.download_media(cdn_url, media.title)
        return download_path
