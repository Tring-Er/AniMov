from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.Media import Media
from AniMov.use_cases.streaming_providers.ProvidersManager import ProvidersManager
from AniMov.use_cases.scraper.WebScraper import WebScraper
from AniMov.use_cases.tasks import Search, TrendingTvShows, TrendingMovies, Quit
from AniMov.use_cases.tasks import Option
from AniMov.interfaces.Cli.CliMessages import CliMessages


class CliManager:

    def __init__(self) -> None:
        self.provider_manager = ProvidersManager()

    def filter_option_result(self, option: str) -> type[Option]:
        match option:
            case "s":
                return Search
            case "ts":
                return TrendingTvShows
            case "tm":
                return TrendingMovies
            case "q":
                return Quit
            case _:
                raise ValueError(f"{option=} is not a valid option")

    def ask_option(self) -> type[Option]:
        print(CliMessages.PRINT_OPTIONS)
        option_choice = input(CliMessages.ASK_OPTION).lower()
        filtered_option = self.filter_option_result(option_choice)
        return filtered_option

    def execute_option(self, option: type[Option]) -> any:
        if option is Quit:
            print(CliMessages.PROGRAM_QUIT)
            return option().compute()
        if option is TrendingMovies:
            print(CliMessages.TRENDING_MOVIES_OPTION_SELECTED)
            return option().compute(HttpClient())
        if option is TrendingTvShows:
            print(CliMessages.TRENDING_TV_SHOWS_OPTION_SELECTED)
            return option().compute(HttpClient())
        if option is Search:
            show_title = input(CliMessages.ASK_FOR_SHOW_TITLE)
            shows = option().compute(HttpClient(), show_title)
            if len(shows) == 0:
                print(CliMessages.NO_SHOW_FOUND)
                self.execute_option(Quit)
            return shows

    def entry_point(self) -> None:
        selected_option = self.ask_option()
        titles_available_data: list[Media] = self.execute_option(selected_option)
        for current_provider in self.provider_manager.providers:
            web_scraper: WebScraper = WebScraper(HttpClient(), current_provider())
            try:
                web_scraper.run(titles_available_data)
                break
            except Exception as e:
                print("[!] An error has occurred | ", e)
                user_choice = input("Switch to another provider? (y or n): ")
                if user_choice == "n":
                    return
