from typing import Type

from animov.elements.HttpClient import HttpClient
from animov.elements.Media import Media
from animov.use_cases.streaming_providers.ProvidersManager import ProvidersManager
from animov.use_cases.tasks import Search, TrendingTvShows, TrendingMovies, Quit, Option
from animov.interfaces.Cli.CliMessages import CliMessages


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
                if show_to_download.show_type == "TV":
                    selected_season = input(f"Please input the season number(total seasons:{show_to_download.number_of_seasons}): ")
                    selected_episode = input(f"Please input the episode number: ")
                    download_path_or_error = self.provider_manager.download_or_play_tv_show(show_to_download, "d", selected_season, selected_episode)
                else:
                    download_path_or_error = self.provider_manager.download_or_play_movie(show_to_download, "d")
                if isinstance(download_path_or_error, ValueError):
                    print(f"[!]  Invalid Choice Entered! | ", str(ValueError()))
                    self.execute_option(Quit)
                if isinstance(download_path_or_error, IndexError):
                    print(f"[!]  This Episode is coming soon! | ", str(IndexError()))
                    self.execute_option(Quit)
                print(f"Downloaded at {download_path_or_error}")
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
                if selected_show.show_type == "TV":
                    selected_season = input(f"Please input the season number(total seasons:{selected_show.number_of_seasons}): ")
                    selected_episode = input(f"Please input the episode number: ")
                    error = self.provider_manager.download_or_play_tv_show(selected_show, "p", selected_season, selected_episode)
                else:
                    error = self.provider_manager.download_or_play_movie(selected_show, "p")
                if isinstance(error, ValueError):
                    print(f"[!]  Invalid Choice Entered! | ", str(error))
                    self.execute_option(Quit)
                if isinstance(error, IndexError):
                    print(f"[!]  Episode unavailable! | ", str(error))
                    self.execute_option(Quit)
                if isinstance(error, ModuleNotFoundError):
                    print(f"[!]Could not play show: MPV not found | {error}")
                    self.execute_option(Quit)
                if isinstance(error, Exception):
                    print(f"Unexpected error | {error}")
                    self.execute_option(Quit)

    def entry_point(self) -> None:
        selected_option: Type[Option] = self.ask_option()
        available_titles_data: list[Media] = self.execute_option(selected_option)
        self.ask_show(available_titles_data)
