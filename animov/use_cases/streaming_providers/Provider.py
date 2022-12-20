from abc import ABC, abstractmethod

from animov.elements.Media import Media
from animov.elements.HttpClient import HttpClient


class Provider(ABC):
    BASE_URL: str
    COOKIES_URL: str
    COOKIES_QUERY: dict
    BASE_MOVIE_CDN_URL: str
    BASE_TV_SHOW_EPISODE_CDN_URL: str

    @abstractmethod
    def __init__(self, html_client: HttpClient) -> None:
        ...

    @abstractmethod
    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        """Get the tv show url"""

    @abstractmethod
    def create_movie_url(self, show_title: str, show_id: int) -> str:
        """Get the movie url"""

    @abstractmethod
    def play_tv_show(self, show: Media, selected_season: str, selected_episode: str) -> None:
        """Play the selected tv show"""

    @abstractmethod
    def download_tv_show(self, show: Media, selected_season: str, selected_episode: str) -> str:
        """Download the selected tv show"""

    @abstractmethod
    def play_movie(self, show: Media) -> None:
        """Play the selected movie"""

    @abstractmethod
    def download_movie(self, show: Media) -> str:
        """Download the selected movie"""
