from typing import Type

from animov.use_cases.streaming_providers.Provider import Provider
from animov.use_cases.streaming_providers.TheFlix import TheFlix

PROVIDERS: list[Type[Provider]] = [TheFlix]
