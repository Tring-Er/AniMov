from abc import ABC, abstractmethod


class Option(ABC):

    @abstractmethod
    def compute(self, *args) -> any:
        """Compute the option"""
