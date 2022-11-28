import httpx
import threading
import sys
import re

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper
from ..utils.keep_alive import KP

sys.path.append("..")
BASE_URL = "https://v2.vidsrc.me"


class VidSrc(WebScraper):
    def __init__(self, base_url=BASE_URL):
        super().__init__(base_url)
        self.base_url = base_url
        self.stream = "https://vidsrc.stream/pro/"
        self.streamh = {"Referer": "https://source.vidsrc.me/",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
        self.headers = {"Referer": "https://v2.vidsrc.me",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
        self.finalheaders = {"Referer": "https://vidsrc.stream/", "Origin": "https://vidsrc.stream",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
        self.keep_alive = KP(self.stream)

    def search(self, q: str = None):
        q = (
            input("[!] Please Enter the name of the Movie: ")
            if q is None
            else q
        )
        return q

    def results(self, html: str) -> list:
        data = httpx.get(f"https://v2.sg.media-imdb.com/suggestion/{html[0]}/{html}.json", headers=self.headers).json()
        ids = [data["d"][i]["id"] for i in range(len(data["d"]))]

        def title_name(num):
            try:
                name = f'{data["d"][num]["l"]}, {data["d"][num]["y"]},'
                return name
            except:
                return f'{data["d"][num]["l"]}, UNKNOWN,'

        title = [title_name(i)
                 for i in range(len(data["d"]))]
        urls = ["/embed/" + data["d"][i]["id"] for i in range(len(data["d"]))]

        def mov_tv(num):
            try:
                if data["d"][num]["qid"].__contains__("tvSeries"):
                    return "TV"
                else:
                    return "MOVIE"
            except:
                return "UNKNOWN"

        mov_or_tv = [mov_tv(i) for i in range(len(data["d"]))]

        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def get_player_iframe(self, embed):
        url = self.base_url + embed
        response = httpx.get(url, headers=self.headers)
        print(url)
        soup = BS(response, "lxml")
        iframe = soup.find("iframe", {"id": "player_iframe"})
        iframe = iframe["src"]
        iframe = iframe.split("/")[4]
        return iframe

    def ask(self, imdb: str):
        response_season = self.client.get(f"https://www.imdb.com/title/{imdb}/episodes")
        soup = BS(response_season, "lxml")
        seasons = soup.find("h3", {"id": "episode_top"}).text.strip("Season")
        season = input(
                f"Please input the season number(total seasons:{seasons}): "
            )
        response_episodes = self.client.get(f"https://www.imdb.com/title/{imdb}/episodes?season={season}")
        soup = BS(response_episodes, "lxml")
        episodes = soup.findAll("div", {"class": "list_item"})
        episode = input(
                f"Please input the episode number(total episodes in season:{season}):{len(episodes)}: "
        )
        return season, episode

    def cdn_url(self, iframe):
        stream = self.stream + iframe
        response = httpx.get(stream, headers=self.streamh).text
        soup = BS(response, "lxml")
        scripts = soup.find_all("script")
        script = scripts[7]
        script = "".join(script)
        path = script.split("=")[4]
        act_link = script.split("=")[3]
        act_link = act_link.split('"')[1]
        path = path.split('"')[0]
        act_link = "https:" + act_link + "=" + path
        print(act_link)
        url = re.findall("""hls\.loadSource['(']['"]([^"']*)['"][')"][;]""", script)[0]
        t1 = threading.Thread(target=self.keep_alive.ping, args=(act_link, self.finalheaders))
        t1.start()
        return url, act_link

    def enabler(self, path):
        test = httpx.get(path, headers=self.finalheaders).text
        return

    def show_download(self, t: list):
        response_seasons = self.client.get(f"https://www.imdb.com/title/{t[self.aid]}/episodes")
        soup = BS(response_seasons, "lxml")
        seasons = soup.find("h3", {"id": "episode_top"}).text.strip("Season")
        for i in range(int(seasons)):
            response_episodes = self.client.get(f"https://www.imdb.com/title/{t[self.aid]}/episodes?season={i + 1}")
            soup = BS(response_episodes, "lxml")
            episodes = soup.findAll("div", {"class": "list_item"})
            for e in range(len(episodes)):
                iframe = self.get_player_iframe(f"{t[self.url]}/{i + 1}-{e + 1}")
                url, enable = self.cdn_url(iframe)
                self.enabler(enable)
                self.download(url, t[self.title], season=i + 1, episode=e + 1)

    def tv_pand_dp(self, infos: list, state: str = "d" or "p" or "sd"):
        if state == "sd":
            self.show_download(infos)
        name = infos[self.title]
        season, episode = self.ask(infos[self.aid])
        iframe = self.get_player_iframe(f"{infos[self.url]}/{season}-{episode}")
        url, enable = self.cdn_url(iframe)
        self.enabler(enable)
        print(url)
        if state == "d":
            self.download(url, name, season=season, episode=episode)
            return
        self.play(url, name)

    def mov_pand_dp(self, infos: list, state: str = "d" or "p" or "sd"):
        name = infos[self.title]
        iframe = self.get_player_iframe(f"{infos[self.url]}")
        url, enable = self.cdn_url(iframe)
        self.enabler(enable)
        if state == "d":
            self.download(url, name)
            return
        if state == "sd":
            print("You can download only Shows with 'sd'")
            return
        self.play(url, name)

    def sand_r(self, q: str = None):
        return self.results(self.search(q))
