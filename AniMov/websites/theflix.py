from sys import exit
import re
import json
import httpx

from bs4 import BeautifulSoup as BS

from AniMov.elements.WebScraper import WebScraper

BASE_URL = "https://theflix.to"


class TheFlix(WebScraper):

    def __init__(self):
        super().__init__(BASE_URL)
        self.cookies = self.create_cookies()
        self.show_id_index = 1
        self.m_available_garbage = -3
        self.t_available_garbage = -2
        self.total_number_of_seasons_index = 4

    def parse(self, text: str):  # text = "This is a TEST"
        first_letter_lowercase = text[0].lower()  # first_letter_lowercase = t
        list_garbage = []  # his is a  T E S T
        for i in text[1:]:  # in "his is a TEST"
            if i.isupper():
                list_garbage.append(f" {i}")
            else:
                list_garbage.append(i)
        garbage = ''.join(list_garbage).lower().rstrip('.')  # "his is a  t e s t"
        name = f"{first_letter_lowercase}{garbage}"  # "this is a  t e s t
        return re.sub("\W+", "-", name)  # "this-is-a--t-e-s-t

    def create_cookies(self):
        url_query = {"affiliateCode": "", "pathname": "/"}
        return httpx.post("https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing", data=url_query).headers["Set-Cookie"]

    def create_junk_list_1(self, show_title: str) -> list:
        return [[self.parse(i["name"]), i["id"], i["available"], "TV", i["numberOfSeasons"]] for i in json.loads(BS(self.client.get(f"https://theflix.to/tv-shows/trending?search={show_title}"), "lxml", ).select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["mainList"]["docs"] if i["available"]]

    def create_junk_list_2(self, show_title: str) -> list:
        return [[self.parse(i["name"]), i["id"], i["available"], "MOVIE"] for i in json.loads(BS(self.client.get(f"https://theflix.to/movies/trending?search={show_title.replace(' ', '+')}"), "lxml",).select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["mainList"]["docs"] if i["available"]]

    def search_available_titles(self) -> list[list]:
        print("[s] Search\n"
              "[ts] Trending TV Shows\n"
              "[tm] Trending Movies\n"
              "[q] Quit\n")
        choice = input("Enter your choice: ").lower()
        if choice == "s":
            show_title = input("[!] Please Enter the name of a Movie or TV Show: ")
            data = []
            for j in self.create_junk_list_1(show_title):
                data.append(j)
            for k in self.create_junk_list_2(show_title):
                data.append(k)
            if len(data) == 0:
                print("No Results found", "Bye!")
                exit(1)
            else:
                return data
        elif choice == "ts":
            return self.trending_tv_shows()
        elif choice == "tm":
            return self.trending_movies()
        elif choice == "q":
            print("Bye!")
            exit(1)

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

    def get_url_and_formatted_data(self, show_title, show_id, selected_season, selected_episode) -> tuple[str, str]:
        return f"{self.base_url}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}", f"{show_title}_S_{selected_season}_EP_{selected_episode}"

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
            exit()
        self.client.set_headers({"Cookie": k})
        link = self.client.get(
            f"https://theflix.to:5679/tv/videos/{episode_id}/request-access?contentUsageType=Viewing"
        ).json()["url"]
        return link, info

    def get_season_info(self, total_number_of_seasons: int, show_id, show_title, cookies: str):
        selected_season = input(f"Please input the season number(total seasons:{total_number_of_seasons}): ")
        self.client.set_headers({"cookie": cookies})
        number_of_episodes_in_the_season = json.loads(BS(self.client.get(f"https://theflix.to/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-1"), "lxml",).select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["numberOfEpisodes"]
        episode = input(f"Please input the episode number: ")
        return selected_season, number_of_episodes_in_the_season, episode

    def send_search_request(self) -> list[list]:
        return self.search_available_titles()

    def mov_pand_dp(self, m: list, state: str = "d" or "p"):
        name = m[self.title_index]
        page = self.page(m)
        url, name = self.cdn_url(page[0], name, self.cookies)
        if state == "d":
            self.download(url, name)
            return
        self.play(url, name)

    def tv_pand_dp(self, show_data: list, state: str = "d" or "p"):
        formatted_show_data = show_data[self.title_index]
        total_number_of_seasons = show_data[self.total_number_of_seasons_index]
        show_id = show_data[self.show_id_index]
        selected_season, total_number_of_episodes, selected_episode = self.get_season_info(total_number_of_seasons, show_id, formatted_show_data, self.cookies)
        url, formatted_show_data = self.get_url_and_formatted_data(formatted_show_data, show_id, selected_season, selected_episode)
        cdn, formatted_show_data = self.cdn_url_ep(url, formatted_show_data, self.cookies)
        if state == "d":
            self.download(cdn, formatted_show_data)
            return
        self.play(cdn, formatted_show_data)
