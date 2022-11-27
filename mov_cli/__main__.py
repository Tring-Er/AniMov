"""This is a test"""

import os
import platform

import click

from mov_cli.utils.scraper import WebScraper
from mov_cli.websites.theflix import Theflix
from mov_cli.websites.vidsrc import Vidsrc
from mov_cli.websites.eja import eja
from mov_cli.websites.ask4movie import Ask4Movie
from mov_cli.websites.ustvgo import ustvgo
from mov_cli.websites.kimcartoon import kimcartoon
from mov_cli.websites.actvid import Actvid
from mov_cli.websites.dopebox import DopeBox
from mov_cli.websites.sflix import Sflix
from mov_cli.websites.solar import Solar
from mov_cli.websites.goal import goal9

from mov_cli.utils.onstartup import startup


calls = {
    "theflix": [Theflix, "https://theflix.to"],
    "vidsrc": [Vidsrc, "https://v2.vidsrc.me"],
    "eja": [eja, "https://eja.tv"],
    "ask4movie": [Ask4Movie, "https://ask4movie.mx"],
    "ustvgo": [ustvgo, "https://ustvgo.tv"],
    "kimcartoon": [kimcartoon, "https://kimcartoon.li"],
    "actvid": [Actvid, "https://www.actvid.com"],
    "sflix": [Sflix, "https://sflix.se"],
    "solar": [Solar, "https://solarmovie.pe"],
    "dopebox": [DopeBox, "https://dopebox.to"],
    "9goal": [goal9, "https://9goal.tv/"],
}


startup.getkey()

if platform.system() == "Windows":
    os.system("color FF")  # Fixes colour in Windows 10 CMD terminal.


@click.command()
@click.option(
    "-p",
    "--provider",
    prompt=f"""\n
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

The name of the provider""",
    help='The name of the provider ex: "theflix"',
    default=f"theflix",
)
@click.option("-q", "--query", default=None, help="Your search query")
@click.option(
    "-r",
    "--result",
    default=None,
    help="The Result Number you want to be played",
    type=int,
)
def movcli(provider, query, result):  # TODO add regex
    try:
        provider_data = calls.get(provider, calls["theflix"])
        provider: WebScraper = provider_data[0](provider_data[1])
        # provider.redo(query) if query is not None else provider.redo()
        provider.redo(query, result)  # if result else provider.redo(query)
    except UnicodeDecodeError:
        print("The Current Provider has changed")
    except Exception as e:
        print("[!] An error has occurred | ", e)


if __name__ == '__main__':
    movcli()
