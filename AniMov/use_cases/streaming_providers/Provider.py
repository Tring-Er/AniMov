from abc import ABC, abstractmethod


class Provider(ABC):

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base url of the provider"""

    @staticmethod
    @abstractmethod
    def parse(text: str) -> str:
        """Parse the name of the film/tv show"""

    @abstractmethod
    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        """Get the tv show url"""

    @abstractmethod
    def create_movie_url(self, show_title: str, show_id: int) -> str:
        """Get the movie url"""
