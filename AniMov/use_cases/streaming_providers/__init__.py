from typing import Type

from AniMov.use_cases.streaming_providers.Provider import Provider
from AniMov.use_cases.streaming_providers.TheFlix import TheFlix

PROVIDERS: list[Type[Provider]] = [TheFlix]
