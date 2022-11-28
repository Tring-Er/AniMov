import os
import platform

from AniMov.utils.scraper import WebScraper
from AniMov.websites.theflix import TheFlix
from AniMov.websites.vidsrc import VidSrc
from AniMov.websites.eja import Eja
from AniMov.websites.ask4movie import Ask4Movie
from AniMov.websites.ustvgo import Ustvgo
from AniMov.websites.kimcartoon import KimCartoon
from AniMov.websites.actvid import Actvid
from AniMov.websites.dopebox import DopeBox
from AniMov.websites.sflix import Sflix
from AniMov.websites.solar import Solar
from AniMov.websites.goal import Goal9
from AniMov.utils.onstartup import get_key


def ani_mov():
    calls = {
        "theflix": [TheFlix, "https://theflix.to"],
        "vidsrc": [VidSrc, "https://v2.vidsrc.me"],
        "eja": [Eja, "https://eja.tv"],
        "ask4movie": [Ask4Movie, "https://ask4movie.mx"],
        "ustvgo": [Ustvgo, "https://ustvgo.tv"],
        "kimcartoon": [KimCartoon, "https://kimcartoon.li"],
        "actvid": [Actvid, "https://www.actvid.com"],
        "sflix": [Sflix, "https://sflix.se"],
        "solar": [Solar, "https://solarmovie.pe"],
        "dopebox": [DopeBox, "https://dopebox.to"],
        "9goal": [Goal9, "https://9goal.tv/"],
    }

    if platform.system() == "Windows":
        os.system("color FF")

    initial_message = """
Movies and Shows:
theflix
actvid
sflix
solar
dopebox
ask4movie

Live TV:
eja
ustvgo / US IP ONLY

Cartoons:
kimcartoon

Sports:
9goal / Football

The name of the provider """

    get_key()

    selected_provider = input(initial_message)
    if selected_provider == "":
        selected_provider = "theflix"
    query = None
    result = None
    try:
        provider_data = calls.get(selected_provider, calls["theflix"])
        provider: WebScraper = provider_data[0](provider_data[1])
        provider.redo(query, result)
    except UnicodeDecodeError as e:
        print("The Current Provider has changed", e)
    except Exception as e:
        print("[!] An error has occurred | ", e)


if __name__ == '__main__':
    ani_mov()
