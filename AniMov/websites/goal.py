from AniMov.elements.WebScraper import WebScraper


BASE_URL = "https://9goal.tv/"


class Goal9(WebScraper):
    def __init__(self, base_url=BASE_URL) -> None:
        super().__init__(base_url)
        self.base_url = base_url
    
    def search_available_titles(self, q):
        q = "q"
        return q

    def results(self, q):
        data_id = self.http_client.get("https://justameanlessdomain.com/v1/match/related").json()["data"][0]["id"]
        response = self.http_client.get(f"https://justameanlessdomain.com/v1/match/{data_id}").json()
        name = response["data"]["name"]
        stream_data = self.http_client.get(f"https://justameanlessdomain.com/v1/match/{data_id}/stream").json()
        streams = stream_data["data"]["play_urls"]
        urls = [streams[i]["url"] for i in range(len(streams))]
        title = [streams[i]["name"] for i in range(len(streams))]
        ids = [streams[i]["role"] for i in range(len(streams))]
        mov_or_tv = [f"{name}" for i in range(len(streams))]
        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def download_or_play_movie(self, m: list, state: str = "d" or "p" or "sd"):
        if state == "sd":
            print("You can't Showdownload Football Match!?")
            return
        if state == "d":
            self.download_show(m[self.url_index], m[self.title_index])
            return
        self.play_show(m[self.url_index], m[self.title_index])
        
    def send_search_request(self, q: str = None):
        return self.results(self.search_available_titles(q))
