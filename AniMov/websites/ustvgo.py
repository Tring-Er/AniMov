import re

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper


BASE_URL = "https://ustvgo.tv"


class Ustvgo(WebScraper):
    def __init__(self, base_url=BASE_URL):
        super().__init__(base_url)
        self.base_url = base_url

    def l_check(self, sender, x):
        try:
            return sender[x].find("a")["href"]
        except:
            return

    def t_check(self, sender, x):
        try:
            return sender[x].find("a").text
        except:
            return

    def results(self, q):
        response = self.client.get(self.base_url)
        soup = BS(response, "lxml")
        sender = soup.findAll("strong")
        title = [self.t_check(sender, i) for i in range(len(sender))]
        id = [i for i in range(len(sender) - 3)]
        url = [self.l_check(sender, i) for i in range(len(sender))]
        channel = ["channel" for i in range(len(sender) - 3)]
        return [list(sublist) for sublist in zip(title, url, id, channel)]
    
    def stream_link(self, uri):
        response = self.client.get(uri)
        soup = BS(response, "lxml")
        div = soup.find("div", {"class": "iframe-container"})
        url = div.find("iframe")["src"]
        self.client.set_headers({"Referer": f"{uri}"})
        response = self.client.get(f"https://ustvgo.tv{url}")
        soup = BS(response, "lxml")
        script = soup.findAll("script", {"type": "text/javascript"})[1]
        script = "".join(script)
        uri = re.findall("""hls_src='([^"']*)';""", script)[0]
        print(uri)
        return uri

    def mov_pand_dp(self, m: list, state: str = "d" or "p" or "sd"):
        name = m[self.title]
        url = self.stream_link(f"{m[self.url]}")
        if state == "d":
            self.download(url, name)
            return
        self.play(url, name)

    def sand_r(self, q: str = None):
        return self.results(q)
