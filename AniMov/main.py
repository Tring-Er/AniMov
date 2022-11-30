import os
import platform

from AniMov.elements.WebScraper import WebScraper
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

DEFAULT_PROVIDER = 1
PROVIDER_OPTIONS = {
    1: [TheFlix, "https://theflix.to"],
    2: [VidSrc, "https://v2.vidsrc.me"],
    3: [Eja, "https://eja.tv"],
    4: [Ask4Movie, "https://ask4movie.mx"],
    5: [Ustvgo, "https://ustvgo.tv"],
    6: [KimCartoon, "https://kimcartoon.li"],
    7: [Actvid, "https://www.actvid.com"],
    8: [Sflix, "https://sflix.se"],
    9: [Solar, "https://solarmovie.pe"],
    10: [DopeBox, "https://dopebox.to"],
    11: [Goal9, "https://9goal.tv/"],
}


def ani_mov():
    if platform.system() == "Windows":
        os.system("color FF")


get_key()

current_provider = DEFAULT_PROVIDER
while True:
    try:
        print(f"Current provider: {PROVIDER_OPTIONS[current_provider][1]}")
        provider_data = PROVIDER_OPTIONS.get(current_provider, PROVIDER_OPTIONS[current_provider])
        provider: WebScraper = provider_data[0](provider_data[1])
        provider.redo()
        break
    except UnicodeDecodeError as error:
        print("The Current Provider has changed", error)
    except Exception as error:
        print("[!] An error has occurred | ", error)
        user_choice = input("Switch to another provider? (y or n): ")
        if user_choice == "n":
            break
        current_provider += 1


if __name__ == '__main__':
    ani_mov()
