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

    def create_cookies(self):
        url_query = {"affiliateCode": "", "pathname": "/"}
        response = self.http_client.post_request("https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing", url_query)
        return response.headers["Set-Cookie"]

    def get_show_cnd_url(self, show_url: str, cookies) -> str:
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_id = json.loads(HtmlParser(self.http_client.get_request(show_url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_url = self.http_client.get_request(f"https://theflix.to:5679/movies/videos/{show_cdn_id}/request-access?contentUsageType=Viewing").json()["url"]
        return show_cdn_url

    def get_episode_cdn_url(self, url, selected_season, selected_episode, cookies):
        self.http_client.set_headers({"Cookie": cookies})
        show_data = json.loads(HtmlParser(self.http_client.get_request(url).text, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = show_data[int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except IndexError:
            print("Episode unavailable",
                  "Bye!",
                  "Maybe try one of the other websites or request the episode to be added by contacting theflix")
            exit()
        self.http_client.set_headers({"Cookie": cookies})
        cdn_url = self.http_client.get_request(f"https://theflix.to:5679/tv/videos/{episode_id}/request-access?contentUsageType=Viewing").json()["url"]
        return cdn_url

    def get_season_info(self, total_number_of_seasons: int, show_id, show_title, cookies: str):
        selected_season = input(f"Please input the season number(total seasons:{total_number_of_seasons}): ")
        self.http_client.set_headers({"cookie": cookies})
        response = self.http_client.get_request(f"https://theflix.to/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-1")
        number_of_episodes_in_the_season = json.loads(HtmlParser(response, "lxml").get("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["numberOfEpisodes"]
        episode = input(f"Please input the episode number: ")
        return selected_season, number_of_episodes_in_the_season, episode

    def download_or_play_movie(self, show: Media, state: str = "d" or "p") -> None:
        show_title = show.title
        show_id = show.show_id
        show_url = self.provider.create_movie_url(show_title, show_id)
        cdn_url = self.get_show_cnd_url(show_url, self.cookies)
        if state == "d":
            MediaDownloader.download_show(cdn_url, show_title)
        else:
            MediaPlayer.play_show(cdn_url, show_title, self.provider.base_url)

    def download_or_play_tv_show(self, show: Media, state: str = "d" or "p") -> None:
        show_title = show.title
        total_number_of_seasons = show.number_of_seasons
        show_id = show.show_id
        selected_season, total_number_of_episodes, selected_episode = self.get_season_info(total_number_of_seasons, show_id, show_title, self.cookies)
        url = self.provider.get_tv_show_url(show_title, show_id, selected_season, selected_episode)
        cdn_url = self.get_episode_cdn_url(url, selected_season, selected_episode, self.cookies)
        if state == "d":
            MediaDownloader.download_show(cdn_url, show_title)
        else:
            MediaPlayer.play_show(cdn_url, show_title, self.provider.base_url)
