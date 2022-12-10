from AniMov.use_cases.streaming_providers.Provider import Provider
from AniMov.use_cases.streaming_providers.TheFlix import TheFlix

NON_INSTANTIATED_PROVIDER = type[Provider]
PROVIDERS: list[NON_INSTANTIATED_PROVIDER] = [TheFlix]
