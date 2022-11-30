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

    #  TODO To understand what this does precisely
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
        option_choice = input("Enter your choice: ").lower()
        if option_choice == "s":
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
        elif option_choice == "ts":
            return self.trending_tv_shows()
        elif option_choice == "tm":
            return self.trending_movies()
        elif option_choice == "q":
            print("Bye!")
            exit(1)

    def create_junk_list_3(self) -> list:
        return [[self.parse(i["name"]), i["id"], i["available"], "TV", i["numberOfSeasons"]] for i in json.loads(BS(self.client.get(f"https://theflix.to/tv-shows/trending"), "lxml",).select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["mainList"]["docs"]if i["available"]]

    def trending_tv_shows(self):
        data = []
        for j in self.create_junk_list_3():
            data.append(j)
        return data

    def create_junk_list_4(self) -> list:
        return [[self.parse(i["name"]), i["id"], "MOVIE", i["available"]] for i in json.loads(BS(self.client.get(f"https://theflix.to/movies/trending"), "lxml").select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["mainList"]["docs"] if i["available"]]

    def trending_movies(self):
        data = []
        for k in self.create_junk_list_4():
            data.append(k)
        return data

    def create_movie_url(self, show_title: str, show_id: str) -> str:
        return f"{self.base_url}/movie/{show_id}-{show_title}"

    def get_url_and_formatted_data(self, show_title, show_id, selected_season, selected_episode) -> tuple[str, str]:
        return f"{self.base_url}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}", f"{show_title}_S_{selected_season}_EP_{selected_episode}"

    def get_show_cnd_url(self, show_url: str, cookies) -> str:
        self.client.set_headers({"Cookie": cookies})
        show_cdn_id = json.loads(BS(self.client.get(show_url).text, "lxml").select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        self.client.set_headers({"Cookie": cookies})
        show_cdn_url = self.client.get(f"https://theflix.to:5679/movies/videos/{show_cdn_id}/request-access?contentUsageType=Viewing").json()["url"]
        return show_cdn_url

    def get_episode_cdn_url(self, url, selected_season, selected_episode, cookies):
        self.client.set_headers({"Cookie": cookies})
        show_data = json.loads(BS(self.client.get(url).text, "lxml").select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = show_data[int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except IndexError:
            print("Episode unavailable",
                  "Bye!",
                  "Maybe try one of the other websites or request the episode to be added by contacting theflix")
            exit()
        self.client.set_headers({"Cookie": cookies})
        cdn_url = self.client.get(f"https://theflix.to:5679/tv/videos/{episode_id}/request-access?contentUsageType=Viewing").json()["url"]
        return cdn_url

    def get_season_info(self, total_number_of_seasons: int, show_id, show_title, cookies: str):
        selected_season = input(f"Please input the season number(total seasons:{total_number_of_seasons}): ")
        self.client.set_headers({"cookie": cookies})
        number_of_episodes_in_the_season = json.loads(BS(self.client.get(f"https://theflix.to/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-1"), "lxml",).select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["numberOfEpisodes"]
        episode = input(f"Please input the episode number: ")
        return selected_season, number_of_episodes_in_the_season, episode

    def send_search_request(self) -> list[list]:
        return self.search_available_titles()

    def download_or_play_movie(self, show_data: list, state: str = "d" or "p") -> None:
        show_title = show_data[self.title_index]
        show_id = show_data[1]
        show_url = self.create_movie_url(show_title, show_id)
        cdn_url = self.get_show_cnd_url(show_url, self.cookies)
        if state == "d":
            self.download_show(cdn_url, show_title)
        else:
            self.play_show(cdn_url, show_title)

    def download_or_play_tv_show(self, show_data: list, state: str = "d" or "p") -> None:
        formatted_show_data = show_data[self.title_index]
        total_number_of_seasons = show_data[self.total_number_of_seasons_index]
        show_id = show_data[self.show_id_index]
        selected_season, total_number_of_episodes, selected_episode = self.get_season_info(total_number_of_seasons, show_id, formatted_show_data, self.cookies)
        url, formatted_show_data = self.get_url_and_formatted_data(formatted_show_data, show_id, selected_season, selected_episode)
        cdn_url = self.get_episode_cdn_url(url, selected_season, selected_episode, self.cookies)
        if state == "d":
            self.download_show(cdn_url, formatted_show_data)
        else:
            self.play_show(cdn_url, formatted_show_data)
