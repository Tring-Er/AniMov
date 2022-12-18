from bs4 import BeautifulSoup


"""A strings, bytes and everything that can support str and/or bytes"""
PARSABLE_OBJECT = any


class HtmlParser:
    """A bs4 BeautifulSoup interface"""

    def __init__(self, parsable_object: PARSABLE_OBJECT, parse_mode: str) -> None:
        self.parser = BeautifulSoup(parsable_object, parse_mode)

    def get(self, selector: str, **kwargs) -> any:
        return self.parser.select(selector, **kwargs)
