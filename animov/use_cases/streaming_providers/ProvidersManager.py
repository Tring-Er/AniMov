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

    def download_or_play_media(self, media: Media, mode: str, **kwargs) -> None | str:
        if mode == "d":
            download_path = self.current_provider.download_media(media, **kwargs)
            return download_path
        self.current_provider.play_media(media, **kwargs)
