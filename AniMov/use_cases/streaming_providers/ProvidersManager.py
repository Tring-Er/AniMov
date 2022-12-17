from AniMov.elements.Media import Media
from AniMov.elements.HttpClient import HttpClient
from AniMov.use_cases.streaming_providers import PROVIDERS
from AniMov.use_cases.streaming_providers import Provider
from AniMov.use_cases.scraper.WebScraper import WebScraper


class ProvidersManager:

    def __init__(self) -> None:
        self.providers = PROVIDERS[:]
        self.current_provider = self.get_provider()

    def get_provider(self) -> Provider:
        current_provider = self.providers[0]
        self.providers.remove(current_provider)
        web_scraper = WebScraper(HttpClient(), current_provider.COOKIES_URL, current_provider.COOKIES_QUERY)
        current_provider_instance = current_provider(web_scraper)
        return current_provider_instance

    def download_or_play_movie(self, show: Media, mode: str) -> str | Exception:
        error_or_path_or_none = self.current_provider.download_or_play_movie(show, mode)
        return error_or_path_or_none

    def download_or_play_tv_show(self, show: Media, mode: str, selected_season: str, selected_episode: str) -> None | str | Exception:
        error_or_path_or_none = self.current_provider.download_or_play_tv_show(show, selected_season, selected_episode, mode)
        return error_or_path_or_none
