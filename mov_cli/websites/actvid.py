import re
import sys
import base64
import hashlib
from Cryptodome.Cipher import AES
from typing import Callable, Any
from urllib import parse as p
from ..utils.scraper import WebScraper
from bs4 import BeautifulSoup as BS
import json
from ..utils.onstartup import startup

sys.path.append("..")

x: Callable[[Any], str] = (
    lambda d: base64.b64encode(d.encode()).decode().replace("\n", "").replace("=", ".")
)


class Actvid(WebScraper):
    def __init__(self, base_url) -> None:
        super().__init__(base_url)
        self.userinput = None
        self.base_url = base_url
        self.rep_key = (
            "6LfV6aAaAAAAAC-irCKNuIS5Nf5ocl5r0K3Q0cdz"  # Google Recaptcha key
        )
        self.rab_domain = x(
            "https://rabbitstream.net:443"
        )
        # encoding and then decoding the url
        # self.redo()
        # IMP: self.client.get/post always returns a response object
        # self.client.post/get -> httpx.response

    def search(self, query: str = None) -> str:
        query = (
            input(self.blue("[!] Please Enter the name of the Movie: "))
            if query is None
            else query
        )
        self.userinput = query
        return self.client.get(f"{self.base_url}/search/{self.parse(query)}").text

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
        r = self.client.get(f"{self.base_url}/ajax/v2/tv/seasons/{series_id}")
        season_ids = [
            i["data-id"] for i in BS(r, "lxml").select(".dropdown-item")
        ]
        season = input(
            self.lmagenta(
                f"Please input the season number(total seasons:{len(season_ids)}): "
            )
        )
        z = f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}"
        rf = self.client.get(z)
        episodes = [i["data-id"] for i in BS(rf, "lxml").select(".nav-item > a")]
        episode = episodes[
            int(
                input(
                    self.lmagenta(
                        f"Please input the episode number(total episodes in season:{season}):{len(episodes)} : "
                    )
                )
            )
            - 1
            ]
        ep = self.get_ep(url=f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}",
                         data_id=f"{episode}")
        return episode, season, ep

    def get_ep(self, url: str, data_id: str):
        source = self.client.get(f"{url}").text

        soup = BS(source, "lxml")

        unformated = soup.find("a", {"data-id": f"{data_id}"})['title']

        formated = unformated.split("Eps")[1]
        formated = formated.split(":")[0]

        return formated

    def cdn_url(self, final_link: str, rabb_id: str) -> str:
        self.client.set_headers({"X-Requested-With": "XMLHttpRequest"})
        data = self.client.get(
            f"{final_link}getSources?id={rabb_id}"
        ).json()
        source = data['sources']
        link = f"{source}"
        if link.endswith("=="):
            n = json.loads(self.decrypt(data['sources'], self.gh_key()))
            return n[0]['file']
        return source[0]['file']

    def server_id(self, mov_id: str) -> str:
        response = self.client.get(f"{self.base_url}/ajax/movie/episodes/{mov_id}")
        soup = BS(response, "lxml")
        return [i["data-linkid"] for i in soup.select(".nav-item > a")][0]

    def ep_server_id(self, ep_id: str) -> str:
        response = self.client.get(
            f"{self.base_url}/ajax/v2/episode/servers/{ep_id}/#servers-list"
        )
        soup = BS(response, "lxml")
        return [i["data-id"] for i in soup.select(".nav-item > a")][0]

    def get_link(self, thing_id: str) -> tuple:
        response = self.client.get(f"{self.base_url}/ajax/get_link/{thing_id}").json()[
            "link"
        ]
        print(response)
        return response, self.rabbit_id(response)

    def rabbit_id(self, url: str) -> tuple:
        parts = p.urlparse(url, allow_fragments=True, scheme="/").path.split("/")
        return re.findall(r'(https:\/\/.*\/embed-4)', url)[0].replace("embed-4", "ajax/embed-4/"), parts[-1]

    ## decryption
    ## Thanks to Twilight

    # def determine_char_enc(self, value):
    #    result = chardet.detect(value)['encoding']
    #    return result

    # websocket simulation

    def gh_key(self):
        with open(f"{startup.winorlinux()}/movclikey.txt") as f:
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
    
    def download(self, series_id: str, name):
        response_season = self.client.get(f"{self.base_url}/ajax/v2/tv/seasons/{series_id}")
        season_ids = [
            i["data-id"] for i in BS(response_season, "lxml").select(".dropdown-item")
        ]
        for s in range(len(season_ids)):
            formatted_link = f"{self.base_url}/ajax/v2/season/episodes/{season_ids[s]}"
            response_formatted_link = self.client.get(formatted_link)
            episodes = [i["data-id"] for i in BS(response_formatted_link, "lxml").select(".nav-item > a")]
            for eps in range(len(episodes)):
                episode = episodes[eps]
                server_id = self.ep_server_id(episode)
                iframe_url, tv_id = self.get_link(server_id)
                iframe_link, iframe_id = self.rabbit_id(iframe_url)
                url = self.cdn_url(iframe_link, iframe_id)
                self.dl(url, name, season=s + 1, episode=eps + 1)

    def tv_pand_dp(self, title: list, state: str = "d" or "p" or "sd"):
        name = title[self.title]
        if state == "sd":
            self.download(title[self.aid], name)
            return
        episode, season, ep = self.ask(title[self.aid])
        server_id = self.ep_server_id(episode)
        iframe_url, tv_id = self.get_link(server_id)
        iframe_link, iframe_id = self.rabbit_id(iframe_url)
        url = self.cdn_url(iframe_link, iframe_id)
        if state == "d":
            self.dl(url, name, season=season, episode=ep)
            return
        self.play(url, name)

    def mov_pand_dp(self, m: list, state: str = "d" or "p" or "sd"):
        name = m[self.title]
        sid = self.server_id(m[self.aid])
        iframe_url, tv_id = self.get_link(sid)
        iframe_link, iframe_id = self.rabbit_id(iframe_url)
        url = self.cdn_url(iframe_link, iframe_id)
        if state == "d":
            self.dl(url, name)
            return
        if state == "sd":
            print("You can download only Shows with 'sd'")
            return
        self.play(url, name)

    def sandr(self, q: str = None):
        return self.results(self.search(q))

    def redo(self, query: str = None, result: int = None):
        return self.display(query)
