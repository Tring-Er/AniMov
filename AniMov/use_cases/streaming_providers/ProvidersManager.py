from typing import Type

from AniMov.elements.Media import Media
from AniMov.elements.HttpClient import HttpClient
from AniMov.use_cases.streaming_providers import PROVIDERS
from AniMov.use_cases.streaming_providers import Provider
from AniMov.use_cases.scraper.WebScraper import WebScraper


class ProvidersManager:

    def __init__(self) -> None:
        self.providers = PROVIDERS[:]
        self.current_provider = self.get_provider()
        self.web_scraper = self.create_web_scraper(self.current_provider)

    def get_provider(self) -> Type[Provider]:
        current_provider = self.providers[0]
        self.providers.remove(current_provider)
        return current_provider

    def create_web_scraper(self, provider: Type[Provider]) -> WebScraper:
        return WebScraper(HttpClient(), provider())

    def download_or_play_movie(self, show: Media, mode: str) -> None | Exception:
        try:
            self.web_scraper.download_or_play_movie(show, mode)
        except Exception as error:
            return error

    def download_or_play_tv_show(self, show: Media, mode: str, selected_season: str, selected_episode: str) -> None | str | Exception:
        error = self.web_scraper.download_or_play_tv_show(show, selected_season, selected_episode, mode)
        return error
