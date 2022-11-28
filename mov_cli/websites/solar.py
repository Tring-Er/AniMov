from bs4 import BeautifulSoup as BS

from .actvid import Actvid


class Solar(Actvid):
    def __init__(self, base_url) -> None:
        super().__init__(base_url)
        self.base_url = base_url
        self.rep_key = "6LeWLCYeAAAAAL1caYzkrIY-M59Vu41vIblXQZ48"
        self.redo()

    def ask(self, series_id):
        response_season = self.client.get(f"{self.base_url}/ajax/v2/tv/seasons/{series_id}")
        season_ids = [
            i["data-id"] for i in BS(response_season, "lxml").select(".dropdown-item")
        ]
        season = input(
            self.lmagenta(
                f"Please input the season number(total seasons:{len(season_ids)}): "
            )
        )
        response_season_ids = self.client.get(
            f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}"
        )
        episodes = [i["data-id"] for i in BS(response_season_ids, "lxml").select(".eps-item")]
        episode = episodes[
            int(
                input(
                    self.lmagenta(
                        f"Please input the episode number(total episodes in season:{season}):{len(episodes)} : "
                    )
                )
            )
            - 1
        ]
        ep = self.get_ep(f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}", episode)
        return episode, season, ep

    def get_ep(self, url, data_id):
        source = self.client.get(f"{url}").text

        soup = BS(source, "lxml")

        unformated = soup.find("a", {"data-id": f"{data_id}"})['title']

        formated = unformated.split("Eps")[1]
        formated = formated.split(":")[0]

        return formated
