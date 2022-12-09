from sys import exit

from AniMov.use_cases.cli_options.Option import Option


class Quit(Option):

    def compute(self) -> None:
        print("Bye!")
        exit(1)
