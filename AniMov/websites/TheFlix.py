from sys import exit
import json
from httpx import post

from bs4 import BeautifulSoup

from AniMov.elements.WebScraper import WebScraper
from AniMov.elements.Show import Show

BASE_URL = "https://theflix.to"


class TheFlix(WebScraper):

    def __init__(self):
        super().__init__(BASE_URL)
        self.cookies = self.create_cookies()

    def parse(self, text: str) -> str:
        parsed_text = text[0].lower()
        for char in text[1:]:
            if char.isupper() and parsed_text[-1] != " ":
                parsed_text += f" {char.lower()}"
            else:
                parsed_text += char.lower()
        return parsed_text.replace(" ", "-")

    def create_cookies(self):
        url_query = {"affiliateCode": "", "pathname": "/"}
        return post("https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing", data=url_query).headers["Set-Cookie"]

    def get_tv_shows(self, show_title: str) -> list[Show]:
        tv_shows = []
        shows_list_response = self.http_client.get(f"https://theflix.to/tv-shows/trending?search={show_title}")
        show_list_json = BeautifulSoup(shows_list_response, "lxml").select("#__NEXT_DATA__")[0].text
        show_list_data = json.loads(show_list_json)["props"]["pageProps"]["mainList"]["docs"]
        for show_data in show_list_data:
            if show_data["available"]:
                show_title = self.parse(show_data["name"])
                show_id = show_data["id"]
                show_type = "TV"
                number_of_seasons = show_data["numberOfSeasons"]
                tv_shows.append(Show(show_title, show_id, show_type, number_of_seasons))
        return tv_shows

    def get_movie_shows(self, show_title: str) -> list[Show]:
        movie_shows = []
        movies_list_response = self.http_client.get(f"https://theflix.to/movies/trending?search={show_title.replace(' ', '+')}")
        movies_list_json = BeautifulSoup(movies_list_response, "lxml", ).select("#__NEXT_DATA__")[0].text
        movie_list_data = json.loads(movies_list_json)["props"]["pageProps"]["mainList"]["docs"]
        for show_data in movie_list_data:
            if show_data["available"]:
                show_title = self.parse(show_data["name"])
                show_id = show_data["id"]
                show_type = "MOVIE"
                movie_shows.append(Show(show_title, show_id, show_type))
        return movie_shows

    def search_available_titles(self) -> list[Show]:
        print("[s] Search\n"
              "[ts] Trending TV Shows\n"
              "[tm] Trending Movies\n"
              "[q] Quit\n")
        option_choice = input("Enter your choice: ").lower()
        if option_choice == "s":
            show_title = input("[!] Please Enter the name of a Movie or TV Show: ")
            data: list[Show] = []
            for j in self.get_tv_shows(show_title):
                data.append(j)
            for k in self.get_movie_shows(show_title):
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

    def get_trending_tv_shows(self) -> list[Show]:
        trending_tv_shows = []
        tv_shows_response = self.http_client.get(f"https://theflix.to/tv-shows/trending")
        tv_shows_json = BeautifulSoup(tv_shows_response, "lxml", ).select("#__NEXT_DATA__")[0].text
        tv_shows_data = json.loads(tv_shows_json)["props"]["pageProps"]["mainList"]["docs"]
        for show_data in tv_shows_data:
            if show_data["available"]:
                show_title = self.parse(show_data["name"])
                show_id = show_data["id"]
                show_type = "TV"
                number_of_seasons = show_data["numberOfSeasons"]
                trending_tv_shows.append(Show(show_title, show_id, show_type, number_of_seasons))
        return trending_tv_shows

    def trending_tv_shows(self) -> list[Show]:
        data = []
        for j in self.get_trending_tv_shows():
            data.append(j)
        return data

    def get_trending_movies(self) -> list[Show]:

        trending_movie_shows = []
        tv_shows_response = self.http_client.get(f"https://theflix.to/movies/trending")
        tv_shows_json = BeautifulSoup(tv_shows_response, "lxml", ).select("#__NEXT_DATA__")[0].text
        tv_shows_data = json.loads(tv_shows_json)["props"]["pageProps"]["mainList"]["docs"]
        for i in tv_shows_data:
            if i["available"]:
                show_title = self.parse(i["name"])
                show_id = i["id"]
                show_type = "MOVIE"
                trending_movie_shows.append(Show(show_title, show_id, show_type))
        return trending_movie_shows

    def trending_movies(self) -> list[Show]:
        data = []
        for k in self.get_trending_movies():
            data.append(k)
        return data

    def create_movie_url(self, show_title: str, show_id: int) -> str:
        return f"{self.base_url}/movie/{show_id}-{show_title}"

    def get_url_and_formatted_data(self, show_title, show_id, selected_season, selected_episode) -> tuple[str, str]:
        return f"{self.base_url}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}", f"{show_title}_S_{selected_season}_EP_{selected_episode}"

    def get_show_cnd_url(self, show_url: str, cookies) -> str:
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_id = json.loads(BeautifulSoup(self.http_client.get(show_url).text, "lxml").select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["movie"]["videos"][0]
        self.http_client.set_headers({"Cookie": cookies})
        show_cdn_url = self.http_client.get(f"https://theflix.to:5679/movies/videos/{show_cdn_id}/request-access?contentUsageType=Viewing").json()["url"]
        return show_cdn_url

    def get_episode_cdn_url(self, url, selected_season, selected_episode, cookies):
        self.http_client.set_headers({"Cookie": cookies})
        show_data = json.loads(BeautifulSoup(self.http_client.get(url).text, "lxml").select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["seasons"]
        try:
            episode_id = show_data[int(selected_season) - 1]["episodes"][int(selected_episode) - 1]["videos"][0]
        except IndexError:
            print("Episode unavailable",
                  "Bye!",
                  "Maybe try one of the other websites or request the episode to be added by contacting theflix")
            exit()
        self.http_client.set_headers({"Cookie": cookies})
        cdn_url = self.http_client.get(f"https://theflix.to:5679/tv/videos/{episode_id}/request-access?contentUsageType=Viewing").json()["url"]
        return cdn_url

    def get_season_info(self, total_number_of_seasons: int, show_id, show_title, cookies: str):
        selected_season = input(f"Please input the season number(total seasons:{total_number_of_seasons}): ")
        self.http_client.set_headers({"cookie": cookies})
        number_of_episodes_in_the_season = json.loads(BeautifulSoup(self.http_client.get(f"https://theflix.to/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-1"), "lxml", ).select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["selectedTv"]["numberOfEpisodes"]
        episode = input(f"Please input the episode number: ")
        return selected_season, number_of_episodes_in_the_season, episode

    def send_search_request(self) -> list[Show]:
        return self.search_available_titles()

    def download_or_play_movie(self, show: Show, state: str = "d" or "p") -> None:
        show_title = show.title
        show_id = show.show_id
        show_url = self.create_movie_url(show_title, show_id)
        cdn_url = self.get_show_cnd_url(show_url, self.cookies)
        if state == "d":
            self.download_show(cdn_url, show_title)
        else:
            self.play_show(cdn_url, show_title)

    def download_or_play_tv_show(self, show: Show, state: str = "d" or "p") -> None:
        formatted_show_data = show.title
        total_number_of_seasons = show.number_of_seasons
        show_id = show.show_id
        selected_season, total_number_of_episodes, selected_episode = self.get_season_info(total_number_of_seasons, show_id, formatted_show_data, self.cookies)
        url, formatted_show_data = self.get_url_and_formatted_data(formatted_show_data, show_id, selected_season, selected_episode)
        cdn_url = self.get_episode_cdn_url(url, selected_season, selected_episode, self.cookies)
        if state == "d":
            self.download_show(cdn_url, formatted_show_data)
        else:
            self.play_show(cdn_url, formatted_show_data)
