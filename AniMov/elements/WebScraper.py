from os import getcwd
from subprocess import Popen
from sys import exit


from AniMov.utils.httpclient import HttpClient


class WebScraper:

    def __init__(self, base_url: str) -> None:
        self.client = HttpClient()
        self.base_url = base_url
        self.title_index = 0
        self.url_index = 1
        self.show_id_index = 2
        self.show_type_index = 3

    @staticmethod
    def parse(txt: str) -> str:
        return txt.lower().replace(" ", "-")

    def download(
            self, url: str, name: str, subtitle: str = None, season=None, episode=None
    ):
        name = self.parse(name)
        fixname = name.replace("-", " ")
        if season or episode is None:
            pass
        else:
            fixname = f"{fixname}S{season}E{episode}"

        args = [
            'ffmpeg',
            '-n',
            '-thread_queue_size',
            '4096',
            '-err_detect',
            'ignore_err',
            '-i',
            f'{url}',
            "-user_agent",
            '"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"',
            '-c',
            'copy',
            '-preset',
            'ultrafast',
            f'{fixname}.mp4'
        ]

        if subtitle:
            args.extend(
                ["-vf", f"subtitle={subtitle}", f"{fixname}.mp4"]
            )
        ffmpeg_process = Popen(args)
        ffmpeg_process.wait()

        return print(f"Downloaded at {getcwd()}")

    def play(self, url: str, name: str):
        try:
            try:
                args = [
                    "mpv",
                    f"--referrer={self.base_url}",
                    f"{url}",
                    f"--force-media-title=mov-cli:{name}",
                    "--no-terminal",
                ]

                mpv_process = Popen(
                    args
                )
                mpv_process.wait()
            except ModuleNotFoundError:
                args = [
                    "vlc",
                    f"--http-referrer={self.base_url}",
                    f"{url}",
                    f"--meta-title=mov-cli{name}",
                    "--no-terminal",
                ]
                vlc_process = Popen(
                    args
                )
                vlc_process.wait()
        except Exception as e:
            print(f"[!]Could not play {name}: MPV or VLC not found | {e}")
            exit(1)

    def search_available_titles(self, q: str = None) -> str:
        pass

    def results(self, data: str) -> list:
        raise NotImplementedError()

    def tv_pand_dp(self, t: list, state: str = "d" or "p"):
        pass

    def mov_pand_dp(self, m: list, state: str = "d" or "p"):
        pass

    def send_search_request(self, q: str = None):
        return self.results(self.search_available_titles(q))

    def display(self):
        titles_available = self.send_search_request()
        for show_index, title_data in enumerate(titles_available, start=1):
            print(f"[{show_index}] {title_data[self.title_index]} {title_data[self.show_type_index]}\n")
        print("[q] Exit!\n"
              "[d] Download!\n"
              "[sd] Download Whole Show!\n")
        choice = None
        while choice not in range(len(titles_available) + 1):
            choice = input("Enter your choice: ")
            if choice == "q":
                exit(1)
            elif choice == "d":
                try:
                    show_to_download_index = int(input("[!] Please enter the number of the movie you want to download: ")) - 1
                    show_to_download_data = titles_available[show_to_download_index]
                    if show_to_download_data[self.show_type_index] == "TV":
                        self.tv_pand_dp(show_to_download_data, "d")
                    else:
                        self.mov_pand_dp(show_to_download_data, "d")
                except ValueError as e:
                    print(
                        f"[!]  Invalid Choice Entered! | ",
                        str(e),
                    )
                    exit(1)
                except IndexError as e:
                    print(
                        f"[!]  This Episode is coming soon! | ",
                        str(e),
                    )
                    exit(1)
            elif choice == "sd":
                try:
                    mov_or_tv = titles_available[
                        int(
                            input(
                                "[!] Please enter the number of the movie you want to download: "
                            )
                        )
                        - 1
                        ]
                    if mov_or_tv[self.show_type_index] == "TV":
                        self.tv_pand_dp(mov_or_tv, "sd")
                    else:
                        self.mov_pand_dp(mov_or_tv, "sd")
                except ValueError as e:
                    print(
                        f"[!]  Invalid Choice Entered! | ",
                        str(e),
                    )
                    exit(1)
                except IndexError as e:
                    print(
                        f"[!]  This Episode is coming soon! | ",
                        str(e),
                    )
                    exit(1)
            else:
                mov_or_tv = titles_available[int(choice) - 1]
                if mov_or_tv[self.show_type_index] == "TV":
                    self.tv_pand_dp(mov_or_tv, "p")
                else:
                    self.mov_pand_dp(mov_or_tv, "p")

    def redo(self):
        self.display()
