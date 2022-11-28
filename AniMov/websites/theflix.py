import re
import sys
import json
import httpx

from bs4 import BeautifulSoup as BS

from AniMov.utils.scraper import WebScraper

sys.path.append("..")


class TheFlix(WebScraper):
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
        print("[s] Search")
        print("[ts] Trending TV Shows")
        print("[tm] Trending Movies")
        print("[q] Quit")
        choice = input("Enter your choice: ").lower()
        if choice == "s":
            q = (
                input("[!] Please Enter the name of the Movie: ")
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
                print("No Results found", "Bye!")
                sys.exit(1)
            else:
                return data
        elif choice == "ts":
            return self.trending_tv_shows()
        elif choice == "tm":
            return self.trending_movies()
        elif choice == "q":
            print("Bye!")
            sys.exit(1)

    def trending_tv_shows(self):
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

    def trending_movies(self):
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

    def page(self, info: list):
        return f"{self.base_url}/movie/{info[1]}-{info[0]}", info[0]

    def ws_page(self, info: list):
        return (
            f"{self.base_url}/tv-show/{info[1]}-{info[0]}/season-{info[-2]}/episode-{info[-1]}",
            f"{info[0]}_S_{info[-2]}_EP_{info[-1]}",
        )

    def cdn_url(self, link, info, k):
        self.client.set_headers({"Cookie": k})
        obj_id = json.loads(
            BS(self.client.get(link).text, "lxml")
            .select("#__NEXT_DATA__")[0]
            .text
        )["props"]["pageProps"]["movie"]["videos"][0]
        self.client.set_headers({"Cookie": k})
        link = self.client.get(
            f"https://theflix.to:5679/movies/videos/{obj_id}/request-access?contentUsageType=Viewing"
        ).json()["url"]
        return link, info

    def get_season_episode(self, link):
        return (
            re.search(r"(?<=season-)\d+", link).group(),
            re.search(r"(?<=episode-)\d+", link).group(),
        )

    def cdn_url_ep(self, link, info, k):
        season, episode = self.get_season_episode(link)
        self.client.set_headers({"Cookie": k})
        f = json.loads(
            BS(self.client.get(link).text, "lxml")
            .select("#__NEXT_DATA__")[0]
            .text
        )["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = f[int(season) - 1]["episodes"][int(episode) - 1]["videos"][0]
        except IndexError:
            print(
                "Episode unavailable",
                "Bye!",
                "Maybe try "
                "one of the "
                "other "
                "websites or "
                "request the "
                "episode to "
                "be added by "
                "contacting "
                "theflix"
            )
            sys.exit()
        self.client.set_headers({"Cookie": k})
        link = self.client.get(
            f"https://theflix.to:5679/tv/videos/{episode_id}/request-access?contentUsageType=Viewing"
        ).json()["url"]
        return link, info

    def ask(self, ts, ids, name, token: str):
        season = input(
            f"Please input the season number(total seasons:{ts}): "
        )
        self.client.set_headers({"cookie": token})
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
            f"Please input the episode number(total episodes in {season}:{episodes // int(ts)}: "
        )
        return season, episodes, episode

    def sand_r(self, q: str = None):
        return self.search(q)

    def mov_pand_dp(self, m: list, state: str = "d" or "p"):
        name = m[self.title]
        self.userinput = f"{name}"
        page = self.page(m)
        url, name = self.cdn_url(page[0], name, self.token)
        if state == "d":
            self.download(url, name)
            return
        self.play(url, name)

    def tv_pand_dp(self, t: list, state: str = "d" or "p"):
        name = t[self.title]
        season, episodes, episode = self.ask(
            t[self.seasons], t[self.aid], name, self.token
        )
        self.userinput = f"{name}"
        page, name = self.ws_page([name, t[1], season, episode])
        cdn, name = self.cdn_url_ep(page, name, self.token)
        if state == "d":
            self.download(cdn, name)
            return
        self.play(cdn, name)
