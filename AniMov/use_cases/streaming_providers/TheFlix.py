from AniMov.use_cases.streaming_providers.Provider import Provider


class TheFlix(Provider):
    BASE_URL = "https://theflix.to"
    COOKIES_URL = "https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing"
    COOKIES_QUERY = {"affiliateCode": "", "pathname": "/"}
    BASE_MOVIE_CDN_URL = "https://theflix.to:5679/movies/videos/{}/request-access?contentUsageType=Viewing"
    BASE_TV_SHOW_EPISODE_CDN_URL = "https://theflix.to:5679/tv/videos/{}/request-access?contentUsageType=Viewing"

    def get_tv_show_url(self, show_title: str, show_id: int, selected_season: str, selected_episode: str) -> str:
        return f"{self.BASE_URL}/tv-show/{show_id}-{show_title}/season-{selected_season}/episode-{selected_episode}"

    def create_movie_url(self, show_title: str, show_id: int) -> str:
        return f"{self.BASE_URL}/movie/{show_id}-{show_title}"
