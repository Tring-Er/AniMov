from AniMov.elements.WebScraper import WebScraper
from AniMov.websites.theflix import TheFlix


DEFAULT_PROVIDER = "theflix"
PROVIDER_OPTIONS = {"theflix": TheFlix}
INITIAL_MESSAGE = "Movies and Shows:\n" \
                  "theflix\n" \
                  "\n" \
                  "The name of the provider "


def ani_mov():
    selected_provider_str = input(INITIAL_MESSAGE)
    selected_provider_obj = PROVIDER_OPTIONS.get(selected_provider_str, PROVIDER_OPTIONS[DEFAULT_PROVIDER])
    try:
        provider_object: WebScraper = selected_provider_obj()
        provider_object.redo()
    except UnicodeDecodeError as e:
        print("The Current Provider has changed", e)
    except Exception as e:
        print("[!] An error has occurred | ", e)


if __name__ == '__main__':
    ani_mov()
