from AniMov.elements.WebScraper import WebScraper
from AniMov.websites.TheFlix import TheFlix
from AniMov.elements.HttpClient import HttpClient

PROVIDER_OPTIONS = [TheFlix]


def ani_mov():
    for provider in PROVIDER_OPTIONS:
        provider_object: WebScraper = provider(HttpClient())
        try:
            provider_object.run()
            break
        except UnicodeDecodeError as e:
            print("The Current Provider has changed", e)
        except Exception as e:
            print("[!] An error has occurred | ", e)
            user_choice = input("Switch to another provider? (y or n): ")
            if user_choice == "n":
                return


if __name__ == '__main__':
    ani_mov()
