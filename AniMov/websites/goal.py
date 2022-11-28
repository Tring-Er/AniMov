from AniMov.elements.WebScraper import WebScraper


class Goal9(WebScraper):
    def __init__(self, base_url) -> None:
        super().__init__(base_url)
        self.base_url = base_url
    
    def search(self, q):
        q = "q"
        return q

    def results(self, q):
        data_id = self.client.get("https://justameanlessdomain.com/v1/match/related").json()["data"][0]["id"]
        response = self.client.get(f"https://justameanlessdomain.com/v1/match/{data_id}").json()
        name = response["data"]["name"]
        stream_data = self.client.get(f"https://justameanlessdomain.com/v1/match/{data_id}/stream").json()
        streams = stream_data["data"]["play_urls"]
        urls = [streams[i]["url"] for i in range(len(streams))]
        title = [streams[i]["name"] for i in range(len(streams))]
        ids = [streams[i]["role"] for i in range(len(streams))]
        mov_or_tv = [f"{name}" for i in range(len(streams))]
        return [list(sublist) for sublist in zip(title, urls, ids, mov_or_tv)]

    def mov_pand_dp(self, m: list, state: str = "d" or "p" or "sd"):
        if state == "sd":
            print("You can't Showdownload Football Match!?")
            return
        if state == "d":
            self.download(m[self.url], m[self.title])
            return
        self.play(m[self.url], m[self.title])
        
    def sand_r(self, q: str = None):
        return self.results(self.search(q))
