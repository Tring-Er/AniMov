from AniMov.use_cases.streaming_providers import NON_INSTANTIATED_PROVIDER, PROVIDERS


class ProvidersManager:

    def __init__(self) -> None:
        self.providers = PROVIDERS
        self.current_provider_index = None

    def set_provider_index(self) -> None:
        if self.current_provider_index is None:
            self.current_provider_index = 0
        else:
            self.current_provider_index += 1

    def get_provider(self) -> NON_INSTANTIATED_PROVIDER:
        self.set_provider_index()
        return self.providers[self.current_provider_index]
