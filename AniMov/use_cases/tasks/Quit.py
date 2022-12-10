from sys import exit

from AniMov.use_cases.tasks.Option import Option


class Quit(Option):

    def compute(self) -> None:
        exit()
