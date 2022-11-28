from os import getcwd
import subprocess
import sys


from AniMov.utils.httpclient import HttpClient


class WebScraper:

    def __init__(self, base_url: str) -> None:
        self.client = HttpClient()
        self.base_url = base_url
        self.title, self.url, self.aid, self.mv_tv = 0, 1, 2, 3
        pass

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
        ffmpeg_process = subprocess.Popen(args)
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

                mpv_process = subprocess.Popen(
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
                vlc_process = subprocess.Popen(
                    args
                )
                vlc_process.wait()
        except Exception as e:
            txt = f"[!]Could not play {name}: MPV or VLC not found | {e}"
            sys.exit(1)

    def search(self, q: str = None) -> str:
        pass

    def results(self, data: str) -> list:
        pass

    def tv_pand_dp(self, t: list, state: str = "d" or "p"):
        pass

    def mov_pand_dp(self, m: list, state: str = "d" or "p"):
        pass

    def sand_r(self, q: str = None):
        return self.results(self.search(q))

    def display(self, q: str = None, result_no: int = None):
        import AniMov.main as movcli
        result = self.sand_r(q)
        for ix, vl in enumerate(result):
            print(
                f"[{ix + 1}] {vl[self.title]} {vl[self.mv_tv]}", end="\n\n"
            )
        print("[q] Exit!", end="\n\n")
        print("[s] Search Again!", end="\n\n")
        print("[d] Download!", end="\n\n")
        print("[p] Switch Provider!", end="\n\n")
        print("[sd] Download Whole Show!", end="\n\n")
        choice = ""
        while choice not in range(len(result) + 1):
            choice = (
                input("Enter your choice: ") if not result_no else result_no
            )
            if choice == "q":
                sys.exit()
            elif choice == "s":
                return self.redo()
            elif choice == "p":
                return movcli.mov_cli()
            elif choice == "d":
                try:
                    mov_or_tv = result[
                        int(
                            input(
                                "[!] Please enter the number of the movie you want to download: "
                            )
                        )
                        - 1
                        ]
                    if mov_or_tv[self.mv_tv] == "TV":
                        self.tv_pand_dp(mov_or_tv, "d")
                    else:
                        self.mov_pand_dp(mov_or_tv, "d")
                except ValueError as e:
                    print(
                        f"[!]  Invalid Choice Entered! | ",
                        str(e),
                    )
                    sys.exit(1)
                except IndexError as e:
                    print(
                        f"[!]  This Episode is coming soon! | ",
                        str(e),
                    )
                    sys.exit(2)
            elif choice == "sd":
                try:
                    mov_or_tv = result[
                        int(
                            input(
                                "[!] Please enter the number of the movie you want to download: "
                            )
                        )
                        - 1
                        ]
                    if mov_or_tv[self.mv_tv] == "TV":
                        self.tv_pand_dp(mov_or_tv, "sd")
                    else:
                        self.mov_pand_dp(mov_or_tv, "sd")
                except ValueError as e:
                    print(
                        f"[!]  Invalid Choice Entered! | ",
                        str(e),
                    )
                    sys.exit(1)
                except IndexError as e:
                    print(
                        f"[!]  This Episode is coming soon! | ",
                        str(e),
                    )
                    sys.exit(2)
            else:
                mov_or_tv = result[int(choice) - 1]
                if mov_or_tv[self.mv_tv] == "TV":
                    self.tv_pand_dp(mov_or_tv, "p")
                else:
                    self.mov_pand_dp(mov_or_tv, "p")

    def redo(self, search: str = None, result: int = None):
        return self.display(search, result)
