import re

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper


BASE_URL = "https://kimcartoon.li"


class KimCartoon(WebScraper):
    def __init__(self, base_url=BASE_URL):
        super().__init__(base_url)
        self.base_url = base_url

    def search_available_titles(self, q: str):
        q = (
            input("[!] Please Enter the name of the Movie: ")
            if q is None
            else q
        )
        return q
    
    def results(self, q):
        response = self.http_client.post(f"{self.base_url}/Search/Cartoon", data={"keyword": q})
        soup = BS(response.text, "lxml")
        div = soup.find("div", {"class": "list-cartoon"})
        cartoons = div.findAll("div", {"class": "item"})
        title = [cartoons[i].find("span").text for i in range(len(cartoons))]
        urls = [cartoons[i].find("a")["href"] for i in range(len(cartoons))]
        ids = [i for i in range(len(cartoons))]
        mov_or_tv = ["TV" if cartoons[i].find("a")["href"].__contains__("Season") else "MOVIE" for i in range(len(cartoons))]
        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def ask(self, url):
        response = self.http_client.get(self.base_url + url)
        soup = BS(response, "lxml")
        table = soup.find("table", {"class": "listing"})
        episodes = table.findAll("a", {"rel": "noreferrer noopener"})
        episode = int(
            input(
                    f"Please input the episode number:{len(episodes)}: "
            )
        )
        url = episodes[len(episodes) - episode]["href"]
        return url, episode
    
    def download_show(self, t: list):
        response = self.http_client.get(self.base_url + t[self.url_index])
        soup = BS(response, "lxml")
        table = soup.find("table", {"class": "listing"})
        episodes = table.findAll("a", {"rel": "noreferrer noopener"})
        for e in range(len(episodes)):
            epi = e + 1
            link = episodes[len(episodes) - epi]["href"]
            url = self.cdn_url(link)
            self.download_show(url, t[self.title_index], episode=e + 1)
    
    def cdn_url(self, url):
        response = self.http_client.get(self.base_url + url).text
        iframe_id = re.findall('''src="https://www.luxubu.review/v/(.*?)"''', response)[0]
        response_post = self.http_client.post(f"https://www.luxubu.review/api/source/{iframe_id}", data=None).json()['data']
        return response_post[-1]["file"]
    
    def mov_table(self, url):
        response = self.http_client.get(self.base_url + url)
        soup = BS(response, "lxml")
        table = soup.find("table", {"class": "listing"})
        url = table.findAll("a", {"rel": "noreferrer noopener"})[0]["href"]
        return url

    def download_or_play_tv_show(self, t: list, state: str = "d" or "p" or "sd"):
        if state == "sd":
            self.download_show(t)
            return
        name = t[self.title_index]
        link, episode = self.ask(t[self.url_index])
        url = self.cdn_url(link)
        if state == "d":
            self.download_show(url, name, season=".", episode=episode)
            return
        self.play_show(url, name)

    def download_or_play_movie(self, m: list, state: str = "d" or "p" or "sd"):
        if state == "sd":
            print("Only Shows can be downloaded with sd")
            return
        name = m[self.title_index]
        link = self.mov_table(f"{m[self.url_index]}")
        url = self.cdn_url(link)
        if state == "d":
            self.download_show(url, name)
            return
        self.play_show(url, name)
