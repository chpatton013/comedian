from ..declaration import Declaration


class PhysicalDevice(Declaration):
    def __init__(self, name: str):
        super().__init__(name, [])
