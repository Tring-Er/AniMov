import json
from sys import exit

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
        self.cookies = self.create_cookies()

    def create_cookies(self) -> str:
        url_query = {"affiliateCode": "", "pathname": "/"}
        response = self.http_client.post_request("https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing", url_query)
        return response.headers["Set-Cookie"]

    def get_show_cnd_url(self, show_url: str, cookies) -> str:
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_id = json.loads(HtmlParser(self.http_client.get_request(show_url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_url = self.http_client.get_request(f"https://theflix.to:5679/movies/videos/{show_cdn_id}/request-access?contentUsageType=Viewing").json()["url"]
        return show_cdn_url

    def get_episode_cdn_url(self, url, selected_season, selected_episode, cookies) -> str | Exception:
        self.http_client.set_headers({"Cookie": cookies})
        show_data = json.loads(HtmlParser(self.http_client.get_request(url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = show_data[int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except Exception as error:
            return error
        self.http_client.set_headers({"Cookie": cookies})
        cdn_url = self.http_client.get_request(f"https://theflix.to:5679/tv/videos/{episode_id}/request-access?contentUsageType=Viewing").json()["url"]
        return cdn_url

    def download_or_play_movie(self, show: Media, state: str = "d" or "p") -> None | str | Exception:
        show_url = self.provider.create_movie_url(show.title, show.show_id)
        cdn_url = self.get_show_cnd_url(show_url, self.cookies)
        if state == "d":
            download_path = MediaDownloader.download_show(cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url, show.title, self.provider.base_url)
            return error

    def download_or_play_tv_show(self, show: Media, selected_season: str, selected_episode: str, state: str = "d" or "p") -> None | str | Exception:
        url = self.provider.get_tv_show_url(show.title, show.show_id, selected_season, selected_episode)
        cdn_url_or_exception = self.get_episode_cdn_url(url, selected_season, selected_episode, self.cookies)
        if isinstance(cdn_url_or_exception, Exception):
            return cdn_url_or_exception
        if state == "d":
            download_path = MediaDownloader.download_show(cdn_url_or_exception, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url_or_exception, show.title, self.provider.base_url)
            if isinstance(error, Exception):
                return error
