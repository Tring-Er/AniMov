import re
import sys
import base64
import hashlib
import json
from Cryptodome.Cipher import AES
from typing import Callable, Any
from urllib import parse as p

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper
from ..utils.onstartup import windows_or_linux

sys.path.append("..")

x: Callable[[Any], str] = (
    lambda d: base64.b64encode(d.encode()).decode().replace("\n", "").replace("=", ".")
)


BASE_URL = "https://www.actvid.com"


class Actvid(WebScraper):
    def __init__(self, base_url=BASE_URL) -> None:
        super().__init__(base_url)
        self.userinput = None
        self.base_url = base_url
        self.rep_key = (
            "6LfV6aAaAAAAAC-irCKNuIS5Nf5ocl5r0K3Q0cdz"  # Google Recaptcha key
        )
        self.rab_domain = x(
            "https://rabbitstream.net:443"
        )

    def search_available_titles(self, query: str = None) -> str:
        query = (
            input("[!] Please Enter the name of the Movie: ")
            if query is None
            else query
        )
        self.userinput = query
        return self.http_client.get(f"{self.base_url}/search/{self.parse(query)}").text

    def results(self, html: str) -> list:
        soup = BS(html, "lxml")
        urls = [i["href"] for i in soup.select(".film-poster-ahref")]
        mov_or_tv = [
            "MOVIE" if i["href"].__contains__("/movie/") else "TV"
            for i in soup.select(".film-poster-ahref")
        ]
        title = [
            re.sub(
                pattern="full|/tv/|/movie/|hd|watch|[0-9]{2,}",
                repl="",
                string=" ".join(i.split("-")),
            )
            for i in urls
        ]
        ids = [i.split("-")[-1] for i in urls]
        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def ask(self, series_id: str) -> tuple:
        response_season = self.http_client.get(f"{self.base_url}/ajax/v2/tv/seasons/{series_id}")
        season_ids = [
            i["data-id"] for i in BS(response_season, "lxml").select(".dropdown-item")
        ]
        season = input(
                f"Please input the season number(total seasons:{len(season_ids)}): "
        )
        link_season_ids = f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}"
        response_season_ids = self.http_client.get(link_season_ids)
        episodes = [i["data-id"] for i in BS(response_season_ids, "lxml").select(".nav-item > a")]
        episode = episodes[
            int(
                input(
                        f"Please input the episode number(total episodes in season:{season}):{len(episodes)} : "
                )
            )
            - 1
            ]
        ep = self.get_ep(url=f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}",
                         data_id=f"{episode}")
        return episode, season, ep

    def get_ep(self, url: str, data_id: str):
        source = self.http_client.get(f"{url}").text

        soup = BS(source, "lxml")

        unformated = soup.find("a", {"data-id": f"{data_id}"})['title']

        formated = unformated.split("Eps")[1]
        formated = formated.split(":")[0]

        return formated

    def cdn_url(self, final_link: str, rabb_id: str) -> str:
        self.http_client.set_headers({"X-Requested-With": "XMLHttpRequest"})
        data = self.http_client.get(
            f"{final_link}getSources?id={rabb_id}"
        ).json()
        source = data['sources']
        link = f"{source}"
        if link.endswith("=="):
            n = json.loads(self.decrypt(data['sources'], self.gh_key()))
            return n[0]['file']
        return source[0]['file']

    def server_id(self, mov_id: str) -> str:
        response = self.http_client.get(f"{self.base_url}/ajax/movie/episodes/{mov_id}")
        soup = BS(response, "lxml")
        return [i["data-linkid"] for i in soup.select(".nav-item > a")][0]

    def ep_server_id(self, ep_id: str) -> str:
        response = self.http_client.get(
            f"{self.base_url}/ajax/v2/episode/servers/{ep_id}/#servers-list"
        )
        soup = BS(response, "lxml")
        return [i["data-id"] for i in soup.select(".nav-item > a")][0]

    def get_link(self, thing_id: str) -> tuple:
        response = self.http_client.get(f"{self.base_url}/ajax/get_link/{thing_id}").json()[
            "link"
        ]
        print(response)
        return response, self.rabbit_id(response)

    def rabbit_id(self, url: str) -> tuple:
        parts = p.urlparse(url, allow_fragments=True, scheme="/").path.split("/")
        return re.findall(r'(https:\/\/.*\/embed-4)', url)[0].replace("embed-4", "ajax/embed-4/"), parts[-1]

    def gh_key(self):
        with open(f"{windows_or_linux()}/animovkey.txt") as f:
            u = f.read()
        return bytes(u, 'utf-8')

    def md5(self, data):
        return hashlib.md5(data).digest()

    def get_key(self, salt, raw_key):
        key = self.md5(raw_key + salt)
        currentkey = key
        while len(currentkey) < 48:
            x = self.md5(key + raw_key + salt)
            currentkey += key
        return currentkey

    def unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def decrypt(self, data, raw_key):
        key = self.get_key(
            base64.b64decode(data)[8:16], raw_key
        )
        dec_key = key[:32]
        iv = key[32:]
        p = AES.new(dec_key, AES.MODE_CBC, iv=iv).decrypt(
            base64.b64decode(data)[16:]
        )
        return self.unpad(p).decode()
    
    def download_show(self, series_id: str, name):
        response_season = self.http_client.get(f"{self.base_url}/ajax/v2/tv/seasons/{series_id}")
        season_ids = [
            i["data-id"] for i in BS(response_season, "lxml").select(".dropdown-item")
        ]
        for s in range(len(season_ids)):
            formatted_link = f"{self.base_url}/ajax/v2/season/episodes/{season_ids[s]}"
            response_formatted_link = self.http_client.get(formatted_link)
            episodes = [i["data-id"] for i in BS(response_formatted_link, "lxml").select(".nav-item > a")]
            for eps in range(len(episodes)):
                episode = episodes[eps]
                server_id = self.ep_server_id(episode)
                iframe_url, tv_id = self.get_link(server_id)
                iframe_link, iframe_id = self.rabbit_id(iframe_url)
                url = self.cdn_url(iframe_link, iframe_id)
                self.download_show(url, name, season=s + 1, episode=eps + 1)

    def download_or_play_tv_show(self, title: list, state: str = "d" or "p" or "sd"):
        name = title[self.title_index]
        if state == "sd":
            self.download_show(title[self.show_id_index], name)
            return
        episode, season, ep = self.ask(title[self.show_id_index])
        server_id = self.ep_server_id(episode)
        iframe_url, tv_id = self.get_link(server_id)
        iframe_link, iframe_id = self.rabbit_id(iframe_url)
        url = self.cdn_url(iframe_link, iframe_id)
        if state == "d":
            self.download_show(url, name, season=season, episode=ep)
            return
        self.play_show(url, name)

    def download_or_play_movie(self, m: list, state: str = "d" or "p" or "sd"):
        name = m[self.title_index]
        sid = self.server_id(m[self.show_id_index])
        iframe_url, tv_id = self.get_link(sid)
        iframe_link, iframe_id = self.rabbit_id(iframe_url)
        url = self.cdn_url(iframe_link, iframe_id)
        if state == "d":
            self.download_show(url, name)
            return
        if state == "sd":
            print("You can download only Shows with 'sd'")
            return
        self.play_show(url, name)

    def send_search_request(self, q: str = None):
        return self.results(self.search_available_titles(q))

    def redo(self, query: str = None, result: int = None):
        return self.display(query)
