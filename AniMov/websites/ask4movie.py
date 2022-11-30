import re
import base64
import httpx

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper


BASE_URL = "https://ask4movie.mx"


class Ask4Movie(WebScraper):
    def __init__(self, base_url=BASE_URL):
        super().__init__(base_url)
        self.base_url = base_url
    
    def search_available_titles(self, q: str = None):
        q = (
            input("[!] Please Enter the name of the Movie: ")
            if q is None
            else q
        )
        return q.replace(" ", "+")  
    
    def results(self, q):
        response = self.http_client.get(f"{self.base_url}/?s={q}")
        soup = BS(response.text, "lxml")
        result = soup.findAll("div", {"class": "item"})

        def checkmov(x):
            if result[x].findAll("a")[1]["href"].__contains__("channel"):
                return "TV"
            elif result[x].findAll("a")[1]["href"].__contains__("season"):
                return "TV"
            else:
                return "MOVIE"
        ids = [i for i in range(len(result))]
        title = [result[i].findAll("a")[1].text for i in range(len(result))]
        urls = [result[i].findAll("a")[1]["href"] for i in range(len(result))]
        mov_or_tv = [checkmov(i) for i in range(len(result))]
        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def get_link(self, url: str):
        response = self.http_client.get(url).text
        regs = re.findall("""dir['"],['"]([^"']*)""", response)[0]
        txt = base64.b64decode(regs)
        txt = txt.decode("utf-8")
        soup = BS(txt, "lxml")
        res_link = soup.find("iframe")["src"]
        res_link = res_link.split("/")[4]
        return res_link

    def ask_direct_season(self, show_url):
        res_link = self.get_link(show_url)
        response = self.http_client.get(f"https://cinegrabber.com/p/{res_link}").text
        soup = BS(response, "lxml")
        season = soup.title.text.split("┋")[1][1:]
        episodes = soup.findAll("span", {"class": "episode"})
        episode = int(input(
                f"Please input the episode number(total episodes in season:{season}):{len(episodes)}: "
        ))
        url = episodes[episode - 1]["data-url"].split("/")[2]
        return url, season, episode

    def ask_season(self, show_url: str):
        response = self.http_client.get(show_url)
        soup = BS(response, "lxml")
        seasons = soup.findAll("div", {"class": "item"})
        season = input(
                f"Please input the season number(total seasons:{len(seasons)}): "
        )
        season = seasons[len(seasons) - int(season)]
        season_link = season.find("a")["href"]
        res_link = self.get_link(season_link)
        response_seasons = self.http_client.get(f"https://cinegrabber.com/p/{res_link}").text
        soup = BS(response_seasons, "lxml")
        season = soup.title.text.split("┋")[1][1:]
        episodes = soup.findAll("span", {"class": "episode"})
        episode = int(
            input(
                    f"Please input the episode number(total episodes in season:{season}):{len(episodes)}: "
            )
        )
        url = episodes[episode - 1]["data-url"].split("/")[2]
        return url, season, episode
    
    def movie(self, url: str):
        return self.get_link(url)
    
    def cdn_url(self, url):
        post_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0", "Referer": f"https://cinegrabber.com/v/{url}", "Origin": "https://cinegrabber.com"}
        url = f"https://cinegrabber.com/api/source/{url}"
        response = httpx.post(url, headers=post_headers).json()
        print(url)
        url = response["data"][len(["data"]) + 1]["file"]
        print(url)
        return url
    
    def direct_show_download(self, t: list):
        res_link = self.get_link(t[self.url_index])
        response = self.http_client.get(f"https://cinegrabber.com/p/{res_link}").text
        soup = BS(response, "lxml")
        season = soup.title.text.split("┋")[1][1:]
        episodes = soup.findAll("span", {"class": "episode"})
        for e in range(len(episodes)):
            url = episodes[e]["data-url"].split("/")[2]
            url = self.cdn_url(url)
            self.download_show(url, t[self.title_index], episode=e + 1, season=season)

    def download_or_play_tv_show(self, t: list, state: str = "d" or "p" or "sd"):
        if state == "sd":
            if t[self.url_index].__contains__("channel"):
                print("Do a Direct Selection on what Season you want to download.")
                return
            else:
                url, season, episode = self.direct_show_download(t)
                return
        if t[self.url_index].__contains__("channel"):
            url, season, episode = self.ask_season(t[self.url_index])
        else:
            url, season, episode = self.ask_direct_season(t[self.url_index])
        name = t[self.title_index]
        url = self.cdn_url(url)
        if state == "d":
            self.download_show(url, name, episode=episode, season=season)
            return
        self.play_show(url, name)

    def download_or_play_movie(self, m: list, state: str = "d" or "p" or "sd"):
        name = m[self.title_index]
        url = self.movie(m[self.url_index])
        url = self.cdn_url(url)
        if state == "d":
            self.download_show(url, name)
            return
        if state == "sd":
            print("You can download only Shows with 'sd'")
            return
        self.play_show(url, name)

    def send_search_request(self, q: str = None):
        return self.results(self.search_available_titles(q))
