from ..utils.httpclient import HttpClient


from bs4 import BeautifulSoup as bs
from lxml import etree


BASE_URL = "https://streamingcommunity.cheap"


class StreamingCommunity:

    def __init__(self):
        self.base_url = BASE_URL
        self.http_client = HttpClient()

    def search(self) -> str:  #Test case = 83-peaky-blinders
        query = input("[!] Please Enter the name of the Movie: ")
        # Replace any space in the show name
        series_name = query.replace(" ", "-").lower()
        # Get the show page
        raw_page = self.http_client.get(f"{self.base_url}/titles/{series_name}/")
        main_page = bs(raw_page.content, "html.parser")
        # Retrieve how many seasons the show has by xpath
        dom = etree.HTML(str(main_page))
        raw_number_of_seasons = dom.xpath("/html/body/div[2]/main/div[1]/div[1]/div[1]/div/div/div[1]/span[2]")[0].text
        number_of_seasons = raw_number_of_seasons.split(" ", 1)[0]

        user_season_choice = input(f"Please input which season you want to watch(total seasons: {number_of_seasons}) ")

        is_done = False
        num = 0
        episodes = 0
        while not is_done:
            if main_page.find_all(class_="slider-tile"):
                episodes += 1
                num += 1
            else:
                is_done = True
            episode = input(
                f'Please input the episode number(total episodes in season {user_season_choice}: {episodes}) ')
            return episode
