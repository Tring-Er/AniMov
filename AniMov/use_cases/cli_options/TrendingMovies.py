import json

from AniMov.elements.Show import Show
from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.HtmlParser import HtmlParser


class TrendingMovies:

    def parse(self, text: str) -> str:
        parsed_text = text[0].lower()
        for char in text[1:]:
            if char.isupper() and parsed_text[-1] != " ":
                parsed_text += f" {char.lower()}"
            else:
                parsed_text += char.lower()
        return parsed_text.replace(" ", "-")

    def get_trending_movies(self, http_client: HttpClient) -> list[Show]:
        trending_movie_shows = []
        tv_shows_response = http_client.get_request(f"https://theflix.to/movies/trending")
        tv_shows_json = HtmlParser(tv_shows_response, "lxml", ).get("#__NEXT_DATA__")[0].text
        tv_shows_data = json.loads(tv_shows_json)["props"]["pageProps"]["mainList"]["docs"]
        for movies_data in tv_shows_data:
            if movies_data["available"]:
                show_title = self.parse(movies_data["name"])
                show_id = movies_data["id"]
                show_type = "MOVIE"
                trending_movie_shows.append(Show(show_title, show_id, show_type))
        return trending_movie_shows

    def compute(self, http_client: HttpClient) -> list[Show]:
        data = []
        for k in self.get_trending_movies(http_client):
            data.append(k)
        return data
