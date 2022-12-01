from os import getcwd
from subprocess import Popen
from sys import exit

from AniMov.utils.HttpClient import HttpClient
from AniMov.elements.Show import Show


class WebScraper:

    def __init__(self, base_url: str, http_client: HttpClient) -> None:
        self.http_client = http_client
        self.base_url = base_url

    @staticmethod
    def parse(txt: str) -> str:
        raise NotImplementedError()

    def download_show(self, cnd_url: str, formatted_show_data: str, subtitle: str = None, season=None, episode=None) -> None:
        another_formatted_show_data = self.parse(formatted_show_data).replace("-", " ")
        if season is not None and episode is not None:
            another_formatted_show_data = f"{another_formatted_show_data}S{season}E{episode}"
        ffmpeg_args = ['ffmpeg',
                       '-n',
                       '-thread_queue_size',
                       '4096',
                       '-err_detect',
                       'ignore_err',
                       '-i',
                       f'{cnd_url}',
                       "-user_agent",
                       '"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"',
                       '-c',
                       'copy',
                       '-preset',
                       'ultrafast',
                       f'{another_formatted_show_data}.mp4']
        if subtitle:
            ffmpeg_args.extend(["-vf", f"subtitle={subtitle}", f"{another_formatted_show_data}.mp4"])
        ffmpeg_process = Popen(ffmpeg_args)
        ffmpeg_process.wait()
        print(f"Downloaded at {getcwd()}")

    def play_show(self, cnd_url: str, show_formatted_data: str):
        try:
            args = ["mpv",
                    f"--referrer={self.base_url}",
                    f"{cnd_url}",
                    f"--force-media-title=mov-cli:{show_formatted_data}",
                    "--no-terminal"]
            mpv_process = Popen(args)
            mpv_process.wait()
        except ModuleNotFoundError:
            print(f"[!]Could not play {show_formatted_data}: MPV not found")
            exit(1)

    def download_or_play_tv_show(self, t: Show, state: str = "d" or "p"):
        raise NotImplementedError()

    def download_or_play_movie(self, m: Show, state: str = "d" or "p"):
        raise NotImplementedError()

    def send_search_request(self):
        raise NotImplementedError()

    def run(self) -> None:
        titles_available_data: list[Show] = self.send_search_request()
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
