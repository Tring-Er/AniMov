from animov.elements.Media import Media
from animov.elements.HttpClient import HttpClient
from animov.use_cases.streaming_providers import PROVIDERS
from animov.use_cases.streaming_providers import Provider


class ProvidersManager:

    def __init__(self) -> None:
        self.providers = PROVIDERS[:]
        self.current_provider = self.get_provider()

    def get_provider(self) -> Provider:
        current_provider = self.providers[0]
        self.providers.remove(current_provider)
        current_provider_instance = current_provider(HttpClient())
        return current_provider_instance

    def download_or_play_movie(self, show: Media, mode: str) -> None | str:
        if mode == "d":
            error_or_path = self.current_provider.download_movie(show)
            return error_or_path
        self.current_provider.play_movie(show)

    def download_or_play_tv_show(self, show: Media, mode: str, selected_season: str, selected_episode: str) -> None | str:
        if mode == "d":
            download_path = self.current_provider.download_tv_show(show, selected_season, selected_episode)
            return download_path
        self.current_provider.play_tv_show(show, selected_season, selected_episode)
