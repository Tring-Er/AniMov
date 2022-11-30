from AniMov.elements.WebScraper import WebScraper
from AniMov.websites.theflix import TheFlix
from AniMov.websites.streamingcommunity import StreamingCommunity

PROVIDER_OPTIONS = [
    StreamingCommunity,
    TheFlix
]


def ani_mov():
    for provider in PROVIDER_OPTIONS:
        try:
            provider_object: WebScraper = provider()
            provider_object.search()
            #provider_object.redo()
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
