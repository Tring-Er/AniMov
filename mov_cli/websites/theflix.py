import re
import sys
import json
import httpx

sys.path.append("..")
from mov_cli.utils.scraper import WebScraper
from bs4 import BeautifulSoup as BS


class Theflix(WebScraper):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.base_url = base_url
        self.token = self.auth_token()
        self.aid = 1
        self.m_available = -3
        self.t_available = -2
        self.seasons = -1
        self.userinput = ""

    def parse(self, text: str):
        name = f"{text[0].lower()}{''.join([f' {i}' if i.isupper() else i for i in text[1:]]).lower().rstrip('.')}"
        return re.sub("\W+", "-", name)
    def auth_token(self):
        return httpx.post(
            "https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing",
            data={"affiliateCode": "", "pathname": "/"},
        ).headers["Set-Cookie"]

    def search(self, query: str = None) -> list:
        print(self.red("[s] Search"))
        print(self.red("[ts] Trending TV Shows"))
        print(self.red("[tm] Trending Movies"))
        print(self.red("[q] Quit"))
        choice = input(self.blue("Enter your choice: ")).lower()
        if choice == "s":
            q = (
                input(self.blue("[!] Please Enter the name of the Movie: "))
                if query is None
                else query
            )
            data = []
            for j in [
                [self.parse(i["name"]), i["id"], i["available"], "TV", i["numberOfSeasons"]]
                for i in json.loads(
                    BS(
                        self.client.get(f"https://theflix.to/tv-shows/trending?search={q}"),
                        "lxml",
                    )
                    .select("#__NEXT_DATA__")[0]
                    .text
                )["props"]["pageProps"]["mainList"]["docs"]
                if i["available"]
            ]:
                data.append(j)
            for k in [
                [self.parse(i["name"]), i["id"], "MOVIE", i["available"]]
                for i in json.loads(
                    BS(
                        self.client.get(
                            f"https://theflix.to/movies/trending?search={q.replace(' ', '+')}"
                        ),
                        "lxml",
                    )
                    .select("#__NEXT_DATA__")[0]
                    .text
                )["props"]["pageProps"]["mainList"]["docs"]
                if i["available"]
            ]:
                data.append(k)
            if not len(data):
                print(self.red("No Results found"), self.lmagenta("Bye!"))
                sys.exit(1)
            else:
                return data
        elif choice == "ts":
            return self.trendingtvshows()
        elif choice == "tm":
            return self.trendingmovies()
        elif choice == "q":
            print(self.red("Bye!"))
            sys.exit(1)

    def trendingtvshows(self):
        data = []
        for j in [
            [self.parse(i["name"]), i["id"], i["available"], "TV", i["numberOfSeasons"]]
            for i in json.loads(
                BS(
                    self.client.get(f"https://theflix.to/tv-shows/trending"),
                    "lxml",
                )
                .select("#__NEXT_DATA__")[0]
                .text
            )["props"]["pageProps"]["mainList"]["docs"]
            if i["available"]
        ]:
            data.append(j)
        return data
    
    def trendingmovies(self):
        data = []
        for k in [
            [self.parse(i["name"]), i["id"], "MOVIE", i["available"]]
            for i in json.loads(
                BS(
                    self.client.get(
                        f"https://theflix.to/movies/trending"
                    ),
                    "lxml",
                )
                .select("#__NEXT_DATA__")[0]
                .text
            )["props"]["pageProps"]["mainList"]["docs"]
            if i["available"]
        ]:
            data.append(k)
        return data

    def page(self, info):
        return f"{self.base_url}/movie/{info[1]}-{info[0]}", info[0]

    def wspage(self, info):
        return (
            f"{self.base_url}/tv-show/{info[1]}-{info[0]}/season-{info[-2]}/episode-{info[-1]}",
            f"{info[0]}_S_{info[-2]}_EP_{info[-1]}",
        )

    def cdnurl(self, link, info, k):
        self.client.set_headers({"Cookie": k})
        objid = json.loads(
            BS(self.client.get(link).text, "lxml")
            .select("#__NEXT_DATA__")[0]
            .text
        )["props"]["pageProps"]["movie"]["videos"][0]
        self.client.set_headers({"Cookie": k})
        link = self.client.get(
            f"https://theflix.to:5679/movies/videos/{objid}/request-access?contentUsageType=Viewing"
        ).json()["url"]
        return link, info

    def get_season_episode(self, link):
        return (
            re.search(r"(?<=season-)\d+", link).group(),
            re.search(r"(?<=episode-)\d+", link).group(),
        )

    def cdnurlep(self, link, info, k):
        s, ep = self.get_season_episode(link)
        self.client.set_headers({"Cookie": k})
        f = json.loads(
            BS(self.client.get(link).text, "lxml")
            .select("#__NEXT_DATA__")[0]
            .text
        )["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            epid = f[int(s) - 1]["episodes"][int(ep) - 1]["videos"][0]
        except IndexError:
            print(
                self.red("Episode unavailable"),
                self.lmagenta("Bye!"),
                self.blue(
                    "Maybe try "
                    "one of the "
                    "other "
                    "websites or "
                    "request the "
                    "episode to "
                    "be added by "
                    "contacting "
                    "theflix"
                ),
            )
            sys.exit()
        self.client.set_headers({"Cookie": k})
        link = self.client.get(
            f"https://theflix.to:5679/tv/videos/{epid}/request-access?contentUsageType=Viewing"
        ).json()["url"]
        return link, info

    def ask(self, ts, ids, name, tok):
        season = input(
            self.lmagenta(f"Please input the season number(total seasons:{ts}): ")
        )
        self.client.set_headers({"cookie": tok})
        episodes = json.loads(
            BS(
                self.client.get(
                    f"https://theflix.to/tv-show/{ids}-{name}/season-{season}/episode-1"
                ),
                "lxml",
            )
            .select("#__NEXT_DATA__")[0]
            .text
        )["props"]["pageProps"]["selectedTv"]["numberOfEpisodes"]
        episode = input(
            self.lmagenta(
                f"Please input the episode number(total episodes in {season}:{episodes // int(ts)}: "
            )
        )
        return season, episodes, episode

    def SandR(self, q: str = None):
        return self.search(q)

    def MOV_PandDP(self, m: list, state: str = "d" or "p"):
        name = m[self.title]
        self.userinput = f"{name}"
        page = self.page(m)
        url, name = self.cdnurl(page[0], name, self.token)
        if state == "d":
            self.dl(url, name)
            return
        self.play(url, name)

    def TV_PandDP(self, t: list, state: str = "d" or "p"):
        name = t[self.title]
        season, episodes, episode = self.ask(
            t[self.seasons], t[self.aid], name, self.token
        )
        self.userinput = f"{name}"
        page, name = self.wspage([name, t[1], season, episode])
        cdn, name = self.cdnurlep(page, name, self.token)
        if state == "d":
            self.dl(cdn, name)
            return
        self.play(cdn, name)
