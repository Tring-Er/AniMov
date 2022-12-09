import json

from AniMov.elements.Media import Media
from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.HtmlParser import HtmlParser
from AniMov.use_cases.cli_options.Option import Option


class Search(Option):

    def parse(self, text: str) -> str:
        parsed_text = text[0].lower()
        for char in text[1:]:
            if char.isupper() and parsed_text[-1] != " ":
                parsed_text += f" {char.lower()}"
            else:
                parsed_text += char.lower()
        return parsed_text.replace(" ", "-")

    def get_tv_shows(self, show_title: str, http_client: HttpClient) -> list[Media]:
        tv_shows = []
        shows_list_response = http_client.get_request(f"https://theflix.to/tv-shows/trending?search={show_title}")
        show_list_json = HtmlParser(shows_list_response, "lxml").get("#__NEXT_DATA__")[0].text
        show_list_data = json.loads(show_list_json)["props"]["pageProps"]["mainList"]["docs"]
        for show_data in show_list_data:
            if show_data["available"]:
                show_title = self.parse(show_data["name"])
                show_id = show_data["id"]
                show_type = "TV"
                number_of_seasons = show_data["numberOfSeasons"]
                tv_shows.append(Media(show_title, show_id, show_type, number_of_seasons))
        return tv_shows

    def get_movie_shows(self, show_title: str, http_client: HttpClient) -> list[Media]:
        movie_shows = []
        movies_list_response = http_client.get_request(f"https://theflix.to/movies/trending?search={show_title.replace(' ', '+')}")
        movies_list_json = HtmlParser(movies_list_response, "lxml", ).get("#__NEXT_DATA__")[0].text
        movie_list_data = json.loads(movies_list_json)["props"]["pageProps"]["mainList"]["docs"]
        for show_data in movie_list_data:
            if show_data["available"]:
                show_title = self.parse(show_data["name"])
                show_id = show_data["id"]
                show_type = "MOVIE"
                movie_shows.append(Media(show_title, show_id, show_type))
        return movie_shows

    def compute(self, http_client: HttpClient) -> list[Media]:
        show_title = input("[!] Please Enter the name of a Movie or TV Show: ")
        data: list[Media] = []
        for j in self.get_tv_shows(show_title, http_client):
            data.append(j)
        for k in self.get_movie_shows(show_title, http_client):
            data.append(k)
        if len(data) == 0:
            print("No Results found", "Bye!")
            exit(1)
        else:
            return data
