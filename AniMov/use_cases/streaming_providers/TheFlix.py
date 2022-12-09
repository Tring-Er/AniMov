from AniMov.use_cases.streaming_providers.Provider import Provider

BASE_URL = "https://theflix.to"


class TheFlix(Provider):

    def __init__(self):
        self.__base_url = BASE_URL

    @property
    def base_url(self) -> str:
        return self.__base_url

    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        return f"{self.base_url}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}"

    def create_movie_url(self, show_title: str, show_id: int) -> str:
        return f"{self.base_url}/movie/{show_id}-{show_title}"
