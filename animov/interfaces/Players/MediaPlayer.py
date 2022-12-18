from subprocess import Popen


class MediaPlayer:

    @staticmethod
    def play_show(url: str, show_title: str, base_url: str) -> None | Exception:
        try:
            args = ["mpv",
                    f"--referrer={base_url}",
                    f"{url}",
                    f"--force-media-title=AniMov:{show_title}",
                    "--no-terminal"]
            mpv_process = Popen(args)
            mpv_process.wait()
        except Exception as error:
            return error
