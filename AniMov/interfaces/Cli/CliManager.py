from typing import Type

from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.Media import Media
from AniMov.use_cases.streaming_providers.ProvidersManager import ProvidersManager
from AniMov.use_cases.tasks import Search, TrendingTvShows, TrendingMovies, Quit, Option
from AniMov.interfaces.Cli.CliMessages import CliMessages


class CliManager:

    def __init__(self) -> None:
        self.provider_manager = ProvidersManager()

    def filter_option_result(self, option: str) -> Type[Option]:
        match option.lower():
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

    def ask_option(self) -> Type[Option]:
        print(CliMessages.PRINT_OPTIONS)
        option_choice = input(CliMessages.ASK_OPTION)
        filtered_option = self.filter_option_result(option_choice)
        return filtered_option

    def execute_option(self, option: Type[Option]) -> any:
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

    def ask_show(self, available_titles_data: list[Media]) -> None:
        for show_index, show in enumerate(available_titles_data, start=1):
            print(f"[{show_index}] {show.title} {show.show_type}\n")
        print("[q] Exit!\n"
              "[d] Download!\n")
        shows_len = len(available_titles_data)
        while True:
            choice = input("Enter your choice: ")
            if choice == "q":
                self.execute_option(Quit)
            elif choice == "d":
                show_to_download_index = int(
                    input("[!] Please enter the number of the movie you want to download: ")) - 1
                show_to_download = available_titles_data[show_to_download_index]
                error = self.provider_manager.download_or_play_show(show_to_download, "d")
                if isinstance(error, ValueError):
                    print(f"[!]  Invalid Choice Entered! | ", str(ValueError()))
                    self.execute_option(Quit)
                if isinstance(error, IndexError):
                    print(f"[!]  This Episode is coming soon! | ", str(IndexError()))
                    self.execute_option(Quit)
            else:
                try:
                    choice = int(choice)
                except ValueError:
                    print("[!] Invalid option")
                    continue
                if choice > shows_len:
                    print("[!] Invalid option")
                    continue
                selected_show = available_titles_data[int(choice) - 1]
                error = self.provider_manager.download_or_play_show(selected_show, "p")
                if isinstance(error, ValueError):
                    print(f"[!]  Invalid Choice Entered! | ", str(ValueError()))
                    self.execute_option(Quit)
                if isinstance(error, IndexError):
                    print(f"[!]  This Episode is coming soon! | ", str(IndexError()))
                    self.execute_option(Quit)

    def entry_point(self) -> None:
        selected_option: Type[Option] = self.ask_option()
        available_titles_data: list[Media] = self.execute_option(selected_option)
        self.ask_show(available_titles_data)
