import urllib

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper


BASE_URL = "https://eja.tv"


class Eja(WebScraper):
    def __init__(self, base_url=BASE_URL):
        super().__init__(base_url)
        self.base_url = base_url
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:80.0) Gecko/20100101 Firefox/80.0"}

    def search_available_titles(self, q: str = None):
        q = (
            input("[!] Enter a Channel: ")
            if q is None
            else q
        )
        return q

    def results(self, q: str) -> list:
        q = q.replace(" ", "+")
        self.http_client.set_headers(self.headers)
        html = self.http_client.get(f"https://eja.tv/?search={q}").text
        soup = BS(html, "lxml")
        col = soup.findAll("div", {"class": "col-sm-4"})
        urls = [col[i].findAll("a")[1]["href"]
                for i in range(len(col))
                ]
        title = [col[i].findAll("a")[1].text
                 for i in range(len(col))
                 ]
        ids = [col[i].findAll("a")[1]["href"].strip("?")
               for i in range(len(col))]
        mov_or_tv = [col[i].findAll("img")[0]["alt"]
                     for i in range(len(col))
                     ]
        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def get_hls(self, url: str):
        link = urllib.request.urlopen(f"https://eja.tv/?{url}").geturl()
        print(link)
        link = "".join(link)
        link = link.split("?")[1]
        link = link.split("#")[0]
        print(link)
        return link

    def download_or_play_movie(self, m: list, state: str = "d" or "p"):
        name = m[self.title_index]
        url = self.get_hls(m[self.show_id_index])
        if state == "d":
            self.download_show(url, name)
            return
        self.play_show(url, name)

    def send_search_request(self, q: str = None):
        return self.results(self.search_available_titles(q))
