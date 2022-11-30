from httpx import get
from threading import Thread
from re import findall

from bs4 import BeautifulSoup

from AniMov.elements.WebScraper import WebScraper
from AniMov.utils.keep_alive import Pinger

BASE_URL = "https://v2.vidsrc.me"


class VidSrc(WebScraper):

    def __init__(self):
        super().__init__(BASE_URL)
        self.base_url = BASE_URL
        self.cdn_partial_link = "https://vidsrc.stream/pro/"
        self.stream_headers = {"Referer": "https://source.vidsrc.me/",
                               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
        self.requests_headers = {"Referer": "https://v2.vidsrc.me",
                                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
        self.cdn_headers = {"Referer": "https://vidsrc.stream/", "Origin": "https://vidsrc.stream",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
        self.site_pinger = Pinger()

    def search_available_titles(self) -> str:
        return input("[!] Please Enter the name of the Movie: ")

    def results(self, show_title: str) -> list:
        shows_data = get(f"https://v2.sg.media-imdb.com/suggestion/{show_title[0]}/{show_title}.json", headers=self.requests_headers).json()
        shows_id = [shows_data["d"][i]["id"] for i in range(len(shows_data["d"]))]

        def get_title(title_index):
            try:
                _show_title = f'{shows_data["d"][title_index]["l"]}, {shows_data["d"][title_index]["y"]},'
                return _show_title
            except:
                return f'{shows_data["d"][title_index]["l"]}, UNKNOWN,'

        shows_title = [get_title(i) for i in range(len(shows_data["d"]))]
        shows_url = ["/embed/" + shows_data["d"][i]["id"] for i in range(len(shows_data["d"]))]

        def get_show_type(show_index):
            try:
                if shows_data["d"][show_index]["qid"].__contains__("tvSeries"):
                    return "TV"
                else:
                    return "MOVIE"
            except:
                return "UNKNOWN"

        shows_type = [get_show_type(i) for i in range(len(shows_data["d"]))]

        return [list(sublist) for sublist in zip(shows_title, shows_url, shows_id, shows_type)]

    def get_player_iframe(self, embed: str) -> str:
        url = self.base_url + embed
        response = get(url, headers=self.requests_headers)
        soup = BeautifulSoup(response, "lxml")
        iframe = soup.find("iframe", {"id": "player_iframe"})
        iframe = iframe["src"]
        iframe = iframe.split("/")[4]
        return iframe

    def select_season_and_episode(self, show_id: str) -> tuple[str, str]:
        response_seasons = self.http_client.get(f"https://www.imdb.com/title/{show_id}/episodes")
        season_soup = BeautifulSoup(response_seasons, "lxml")
        number_of_seasons = season_soup.find("h3", {"id": "episode_top"}).text.strip("Season")
        selected_season = input(f"Please input the season number(total seasons:{number_of_seasons}): ")
        response_episodes = self.http_client.get(f"https://www.imdb.com/title/{show_id}/episodes?season={selected_season}")
        episodes_soup = BeautifulSoup(response_episodes, "lxml")
        number_of_episodes = episodes_soup.findAll("div", {"class": "list_item"})
        selected_episode = input(f"Please input the episode number(total episodes in season:{selected_season}):{len(number_of_episodes)}: ")
        return selected_season, selected_episode

    def create_cdn_url(self, iframe: str) -> tuple[str, str]:
        stream = self.cdn_partial_link + iframe
        stream_response = get(stream, headers=self.stream_headers).text
        soup_stream = BeautifulSoup(stream_response, "lxml")
        stream_scripts = soup_stream.find_all("script")
        stream_script = "".join(stream_scripts[7])
        path = stream_script.split("=")[4].split('"')[0]
        partial_url_to_ping = stream_script.split("=")[3].split('"')[1]
        url_to_ping = "https:" + partial_url_to_ping + "=" + path
        cdn_url = findall("""hls\.loadSource['(']['"]([^"']*)['"][')"][;]""", stream_script)[0]
        ping_thread = Thread(target=self.site_pinger.ping, args=(url_to_ping, self.cdn_headers))
        ping_thread.start()
        return cdn_url, url_to_ping

    def ping_enabler(self, path: str) -> None:
        get(path, headers=self.cdn_headers)

    def show_download(self, t: list):
        response_seasons = self.http_client.get(f"https://www.imdb.com/title/{t[self.show_id_index]}/episodes")
        soup = BeautifulSoup(response_seasons, "lxml")
        seasons = soup.find("h3", {"id": "episode_top"}).text.strip("Season")
        for i in range(int(seasons)):
            response_episodes = self.http_client.get(f"https://www.imdb.com/title/{t[self.show_id_index]}/episodes?season={i + 1}")
            soup = BeautifulSoup(response_episodes, "lxml")
            episodes = soup.findAll("div", {"class": "list_item"})
            for e in range(len(episodes)):
                iframe = self.get_player_iframe(f"{t[self.url_index]}/{i + 1}-{e + 1}")
                url, enable = self.create_cdn_url(iframe)
                self.ping_enabler(enable)
                self.download_show(url, t[self.title_index], season=i + 1, episode=e + 1)

    def download_or_play_tv_show(self, show_data: list, state: str = "d" or "p") -> None:
        show_title = show_data[self.title_index]
        show_id = show_data[self.show_id_index]
        selected_season, selected_episode = self.select_season_and_episode(show_id)
        iframe = self.get_player_iframe(f"{show_data[self.url_index]}/{selected_season}-{selected_episode}")
        cdn_url, pinging_url = self.create_cdn_url(iframe)
        self.ping_enabler(pinging_url)
        if state == "d":
            self.download_show(cdn_url, show_title, season=selected_season, episode=selected_episode)
        else:
            self.play_show(cdn_url, show_title)

    def download_or_play_movie(self, show_data: list, state: str = "d" or "p") -> None:
        show_title = show_data[self.title_index]
        iframe = self.get_player_iframe(f"{show_data[self.url_index]}")
        cdn_url, pinging_url = self.create_cdn_url(iframe)
        self.ping_enabler(pinging_url)
        if state == "d":
            self.download_show(cdn_url, show_title)
        else:
            self.play_show(cdn_url, show_title)
