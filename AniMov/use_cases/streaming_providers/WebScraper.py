from sys import exit

from AniMov.elements.HttpClient import HttpClient
from AniMov.elements.Show import Show


class WebScraper:

    def __init__(self, base_url: str, http_client: HttpClient) -> None:
        self.http_client = http_client
        self.base_url = base_url

    @staticmethod
    def parse(txt: str) -> str:
        raise NotImplementedError()

    def download_or_play_tv_show(self, t: Show, state: str = "d" or "p"):
        raise NotImplementedError()

    def download_or_play_movie(self, m: Show, state: str = "d" or "p"):
        raise NotImplementedError()

    def run(self, titles_available_data: list[Show]) -> None:
        for show_index, show in enumerate(titles_available_data, start=1):
            print(f"[{show_index}] {show.title} {show.show_type}\n")
        print("[q] Exit!\n"
              "[d] Download!\n")
        choice = None
        while choice not in range(len(titles_available_data) + 1):
            choice = input("Enter your choice: ")
            if choice == "q":
                exit(1)
            elif choice == "d":
                try:
                    show_to_download_index = int(input("[!] Please enter the number of the movie you want to download: ")) - 1
                    show_to_download = titles_available_data[show_to_download_index]
                    if show_to_download.show_type == "TV":
                        self.download_or_play_tv_show(show_to_download, "d")
                    else:
                        self.download_or_play_movie(show_to_download, "d")
                except ValueError as e:
                    print(f"[!]  Invalid Choice Entered! | ", str(e))
                    exit(1)
                except IndexError as e:
                    print(f"[!]  This Episode is coming soon! | ", str(e))
                    exit(1)
            else:
                selected_show = titles_available_data[int(choice) - 1]
                if selected_show.show_type == "TV":
                    self.download_or_play_tv_show(selected_show, "p")
                else:
                    self.download_or_play_movie(selected_show, "p")
