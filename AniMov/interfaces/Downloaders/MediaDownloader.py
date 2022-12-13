from os import getcwd
from subprocess import Popen


class MediaDownloader:

    @staticmethod
    def download_show(cnd_url: str, file_name: str) -> str:
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
                       f'{file_name}.mp4']
        ffmpeg_process = Popen(ffmpeg_args)
        ffmpeg_process.wait()
        return getcwd()
