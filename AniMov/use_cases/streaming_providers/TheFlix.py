from AniMov.use_cases.streaming_providers.Provider import Provider
from AniMov.use_cases.scraper.WebScraper import WebScraper
from AniMov.elements.Media import Media
from AniMov.interfaces.Downloaders.MediaDownloader import MediaDownloader
from AniMov.interfaces.Players.MediaPlayer import MediaPlayer


class TheFlix(Provider):
    BASE_URL = "https://theflix.to"
    COOKIES_URL = "https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing"
    COOKIES_QUERY = {"affiliateCode": "", "pathname": "/"}
    BASE_MOVIE_CDN_URL = "https://theflix.to:5679/movies/videos/{}/request-access?contentUsageType=Viewing"
    BASE_TV_SHOW_EPISODE_CDN_URL = "https://theflix.to:5679/tv/videos/{}/request-access?contentUsageType=Viewing"

    def __init__(self, web_scraper: WebScraper) -> None:
        self.web_scraper = web_scraper

    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        return f"{self.BASE_URL}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}"

    def create_movie_url(self, show_title: str, show_id: int) -> str:
        return f"{self.BASE_URL}/movie/{show_id}-{show_title}"

    def download_or_play_tv_show(self, show: Media, selected_season: str, selected_episode: str, mode: str) -> None | str | Exception:
        url = self.get_tv_show_url(show.title, show.show_id, selected_season, selected_episode)
        episode_cdn_id_or_exception = self.web_scraper.get_episode_cdn_id(url, selected_season, selected_episode)
        if isinstance(episode_cdn_id_or_exception, Exception):
            return episode_cdn_id_or_exception
        cdn_url = self.web_scraper.get_episode_cdn_url(self.BASE_TV_SHOW_EPISODE_CDN_URL, episode_cdn_id_or_exception)
        if mode == "d":
            download_path = MediaDownloader.download_show(cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url, show.title, self.BASE_URL)
            if isinstance(error, Exception):
                return error

    def download_or_play_movie(self, show: Media, mode: str) -> None | str | Exception:
        show_url = self.create_movie_url(show.title, show.show_id)
        show_cdn_id = self.web_scraper.get_movie_cdn_id(show_url)
        cdn_url = self.web_scraper.get_movie_cnd_url(self.BASE_MOVIE_CDN_URL, show_cdn_id)
        if mode == "d":
            download_path = MediaDownloader.download_show(cdn_url, show.title)
            return download_path
        else:
            error = MediaPlayer.play_show(cdn_url, show.title, self.BASE_URL)
            return error
