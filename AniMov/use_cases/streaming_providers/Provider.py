from abc import ABC, abstractmethod


class Provider(ABC):

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base url of the provider"""

    @abstractmethod
    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        """Get the tv show url"""

    @abstractmethod
    def create_movie_url(self, show_title: str, show_id: int) -> str:
        """Get the movie url"""
