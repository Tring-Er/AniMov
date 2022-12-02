from AniMov.use_cases.streaming_providers.WebScraper import WebScraper
from AniMov.use_cases.streaming_providers import provider_list
from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.Show import Show
import AniMov.use_cases.cli_options as cli_options


class CliManager:

    def filter_option_result(self,
                             option: str
                             ) -> cli_options.Search | \
                                  cli_options.TrendingTvShows | \
                                  cli_options.TrendingMovies | \
                                  cli_options.Quit:
        match option:
            case "s":
                return cli_options.Search()
            case "ts":
                return cli_options.TrendingTvShows()
            case "tm":
                return cli_options.TrendingMovies()
            case "q":
                return cli_options.Quit()
            case _:
                raise ValueError(f"{option=} is not a valid option")

    def ask_option(self
                   ) -> cli_options.Search | \
                        cli_options.TrendingTvShows | \
                        cli_options.TrendingMovies | \
                        cli_options.Quit:
        print("[s] Search\n"
              "[ts] Trending TV Shows\n"
              "[tm] Trending Movies\n"
              "[q] Quit\n")
        option_choice = input("Enter your choice: ").lower()
        filtered_option = self.filter_option_result(option_choice)
        return filtered_option

    def entry_point(self) -> None:
        option_choice = self.ask_option()
        for provider in provider_list:
            current_provider: WebScraper = provider(HttpClient())
            try:
                titles_available_data: list[Show] = option_choice.compute(HttpClient())
                current_provider.run(titles_available_data)
                break
            except Exception as e:
                print("[!] An error has occurred | ", e)
                user_choice = input("Switch to another provider? (y or n): ")
                if user_choice == "n":
                    return
