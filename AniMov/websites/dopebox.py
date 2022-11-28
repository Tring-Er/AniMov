from bs4 import BeautifulSoup as BS

from .actvid import Actvid


class DopeBox(Actvid):
    def __init__(self, base_url) -> None:
        super().__init__(base_url)
        self.base_url = base_url
        self.rep_key = "6LeWLCYeAAAAAL1caYzkrIY-M59Vu41vIblXQZ48"

    def ask(self, series_id):
        response_series_id = self.client.get(f"{self.base_url}/ajax/v2/tv/seasons/{series_id}")
        season_ids = [
            i["data-id"] for i in BS(response_series_id, "lxml").select(".dropdown-item")
        ]
        season = input(
                f"Please input the season number(total seasons:{len(season_ids)}): "
        )
        response_episodes = self.client.get(
            f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}"
        )
        episodes = [i["data-id"] for i in BS(response_episodes, "lxml").select(".episode-item")]
        episode = episodes[
            int(
                input(
                        f"Please input the episode number(total episodes in season:{season}):{len(episodes)} : "
                )
            )
            - 1
        ]
        ep = self.get_ep(f"{self.base_url}/ajax/v2/season/episodes/{season_ids[int(season) - 1]}", data_id=episode)
        return episode, season, ep

    def get_ep(self, url, data_id):
        source = self.client.get(f"{url}").text
        soup = BS(source, "lxml")

        unformated = soup.find("div", {"data-id": f"{data_id}"})

        children = unformated.findChildren("div", {"class": "episode-number"})
        for child in children:
            text = child.text

        text = text.split("Episode")[1]
        text = text.split(":")[0]

        return text

    def server_id(self, mov_id):
        response = self.client.get(f"{self.base_url}/ajax/movie/episodes/{mov_id}")
        soup = BS(response, "lxml")
        return [i["data-id"] for i in soup.select(".link-item")][0]

    def ep_server_id(self, ep_id):
        response = self.client.get(
            f"{self.base_url}/ajax/v2/episode/servers/{ep_id}/#servers-list"
        )
        soup = BS(response, "lxml")
        return [i["data-id"] for i in soup.select(".link-item")][0]
