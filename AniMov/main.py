import os
import platform

from AniMov.elements.WebScraper import WebScraper
from AniMov.websites.theflix import TheFlix
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


DEFAULT_PROVIDER = "theflix"
PROVIDER_OPTIONS = {
    "theflix": TheFlix,
    "eja": Eja,
    "ask4movie": Ask4Movie,
    "ustvgo": Ustvgo,
    "kimcartoon": KimCartoon,
    "actvid": Actvid,
    "sflix": Sflix,
    "solar": Solar,
    "dopebox": DopeBox,
    "9goal": Goal9,
}

INITIAL_MESSAGE = """
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


def ani_mov():
    if platform.system() == "Windows":
        os.system("color FF")

    get_key()

    selected_provider = input(INITIAL_MESSAGE)
    provider = PROVIDER_OPTIONS.get(selected_provider, PROVIDER_OPTIONS[DEFAULT_PROVIDER])
    try:
        provider_object: WebScraper = provider()
        provider_object.redo()
    except UnicodeDecodeError as e:
        print("The Current Provider has changed", e)
    except Exception as e:
        print("[!] An error has occurred | ", e)


if __name__ == '__main__':
    ani_mov()
