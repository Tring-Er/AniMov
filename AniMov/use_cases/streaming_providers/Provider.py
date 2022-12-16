from abc import ABC, abstractmethod


class Provider(ABC):
    BASE_URL: str
    COOKIES_URL: str
    COOKIES_QUERY: dict
    BASE_MOVIE_CDN_URL: str
    BASE_TV_SHOW_EPISODE_CDN_URL: str

    @abstractmethod
    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        """Get the tv show url"""

    @abstractmethod
    def create_movie_url(self, show_title: str, show_id: int) -> str:
        """Get the movie url"""
