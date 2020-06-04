from ..declaration import Declaration


class Root(Declaration):
    def __init__(self):
        super().__init__("/", [])
