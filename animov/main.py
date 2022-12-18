from animov.interfaces.Cli.CliManager import CliManager


def main() -> None:
    cli = CliManager()
    cli.entry_point()


if __name__ == '__main__':
    main()
