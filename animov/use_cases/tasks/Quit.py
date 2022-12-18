from sys import exit

from animov.use_cases.tasks.Option import Option


class Quit(Option):

    def compute(self) -> None:
        exit()
