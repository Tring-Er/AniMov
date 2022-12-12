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

    def download_or_play_show(self, show_to_download: Media, mode: str) -> None | Exception:
        try:
            if show_to_download.show_type == "TV":
                self.web_scraper.download_or_play_tv_show(show_to_download, mode)
            else:
                self.web_scraper.download_or_play_movie(show_to_download, mode)
        except Exception as error:
            return error
