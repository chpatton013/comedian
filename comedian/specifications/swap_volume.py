from ..declaration import Declaration


class SwapVolume(Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name, [device])
        self.device = device
