import platform
from os import environ, getlogin

import httpx


def windows_or_linux():
    plt = platform.system()
    if plt == "Windows":
        return f'{environ["USERPROFILE"]}'
    elif plt == "Linux":
        return f"/home/{getlogin()}"
    elif plt == "Darwin":
        return f"/Users/{getlogin()}"


def get_key():
    dokicloud_github_link = "https://api.github.com/repos/consumet/rapidclown/commits/dokicloud"
    rabbitstream_github_link = "https://api.github.com/repos/consumet/rapidclown/commits/rabbitstream"
    dokicloud_github_json = httpx.get(dokicloud_github_link).json()
    rabbitstream_github_json = httpx.get(rabbitstream_github_link).json()
    dokicloud_commit_date = dokicloud_github_json["commit"]["author"]["date"]
    rabbitstream_commit_date = rabbitstream_github_json["commit"]["author"]["date"]
    if dokicloud_commit_date > rabbitstream_commit_date:
        decryptkey_link = "https://raw.githubusercontent.com/consumet/rapidclown/dokicloud/key.txt"
    else:
        decryptkey_link = "https://raw.githubusercontent.com/consumet/rapidclown/rabbitstream/key.txt"
    decryptkey = httpx.get(decryptkey_link).text
    with open(f"{windows_or_linux()}/animovkey.txt", "w") as f:
        f.write(decryptkey)
