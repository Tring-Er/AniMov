from abc import ABC, abstractmethod

from animov.elements.Media import Media
from animov.elements.HttpClient import HttpClient


class Provider(ABC):
    BASE_URL: str
    COOKIES_URL: str
    COOKIES_QUERY: dict
    BASE_MEDIA_URL: str
    BASE_MEDIA_CDN_URL: str

    @abstractmethod
    def __init__(self, html_client: HttpClient) -> None:
        ...

    @abstractmethod
    def create_media_url(self, media: Media, **kwargs) -> str:
        """Create the media url"""

    @abstractmethod
    def create_media_cdn_url(self, media: Media, media_cdn_id: str) -> str:
        """Create the media cdn url"""

    @abstractmethod
    def play_media(self, media: Media, **kwargs) -> None:
        """Play the selected Media"""

    @abstractmethod
    def download_media(self, media: Media, **kwargs) -> str:
        """Download the selected Media"""
