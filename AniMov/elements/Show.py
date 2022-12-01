class Show:

    def __init__(self, title: str, show_id: int, show_type: str, number_of_seasons: int = None) -> None:
        self.title = title
        self.show_id = show_id
        self.show_type = show_type
        self.number_of_seasons = number_of_seasons
