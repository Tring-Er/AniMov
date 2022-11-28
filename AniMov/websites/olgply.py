import sys

from AniMov.elements.WebScraper import WebScraper
from ..utils.dbs import *

sys.path.append("..")


class OlgPly(WebScraper):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.base_url = base_url

    def search(self, q: str = None) -> list:
        q = (
            input("[!] Please Enter the name of the Movie: ")
            if q is None
            else q
        )
        return get_tmdb_id(q)

    def cdn_url(self, name):
        imdb_id = get_imdb_id(name)
        response = httpx.get(
            f"https://olgply.com/api/?imdb={imdb_id}",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux "
                              "x86_64; rv:100.0) "
                              "Gecko/20100101 "
                              "Firefox/100.0"
            },
        ).text
        url = re.findall(r"https?:[a-zA-Z\d.+-/#~]+\.mp4", response)
        print(url)
        return url[0], name

    def cdn_url_ws(self, season, episode, name):
        imdb_id = get_imdb_id(name)
        print(
            f"https://olgply.com/api/?imdb={imdb_id}&season={season}&episode={episode}"
        )
        req = httpx.get(
            f"https://olgply.com/api/?imdb={imdb_id}&season={season}&episode={episode}",
            headers={
                "User-Agent": "Mozilla"
                              "/5.0 ("
                              "X11; "
                              "Linux "
                              "x86_64; "
                              "rv:100"
                              ".0) "
                              "Gecko"
                              "/20100101 Firefox/100.0"
            },
        ).text
        url = re.findall(r"https?:[a-zA-Z\d_.+-/#~]+\.mp4", req)
        print(url)
        return url[0], name

    def ask(self, tmdb_id: str, name: str):
        seasons = get_season_seasons(tmdb_id, name)
        season = input(
            f"Please input the season number(total seasons:{seasons}): "
        )
        episodes = get_season_episodes(tmdb_id, name, season)
        episode = input(
                f"Please input the episode number(total episodes:{episodes}): "
        )
        return self.cdn_url_ws(season, episode, f"{name}_S{season}_E{episode}")

    def display(self, result):
        for ix, vl in enumerate(result):
            print(f"[{ix + 1}] {vl[0]} {vl[-1]}", end="\n\n")
        print("[q] Exit!", end="\n\n")
        print("[s] Search Again!", end="\n\n")
        print("[d] Download!", end="\n\n")
        choice = ""
        while choice not in range(len(result) + 1):
            choice = input("Enter your choice: ")
            if choice == "q":
                sys.exit()
            elif choice == "s":
                return self.redo()
            elif choice == "d":
                try:
                    mov = result[
                        int(
                            input(
                                    "[!] Please enter the number of the movie you want to download: "
                            )
                        )
                        - 1
                        ]
                    name = mov[0]
                    if mov[-1] == "TV":
                        cdn_url, name = self.ask(mov[2], name)
                        self.download(cdn_url, name)
                    else:
                        cdn, name = self.cdn_url(name)
                        self.download(cdn, name)
                except ValueError as e:
                    print(
                        f"[!]  Invalid Choice Entered! | ",
                        str(e),
                    )
                    sys.exit(1)
                except IndexError as e:
                    print(
                        f"[!]  This Episode / Movie is coming soon! | ",
                        str(e),
                    )
                    sys.exit(2)
            else:
                selection = result[int(choice) - 1]
                if selection[-1] == "TV":
                    cdn_url, name = self.ask(selection[2], selection[0])
                    self.play(cdn_url, name)
                else:
                    cdn, name = self.cdn_url(selection[0])
                    self.play(cdn, name)

    def redo(self, query: str = None, result: int = None):
        if query is None:
            return self.display(self.search())
        else:
            return self.display(self.search(query))
