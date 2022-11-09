class ConfItem(object):
    """
    A data model to store information about a configuration item.

    Attributes:
        name (str):
        type (str):
        value (str):
    """

    def __init__(self, name: str = "", type: str = "", value: str = "") -> None:
        self.name: str = name
        self.type: str = type
        self.value: str = value

    def __eq__(self, __o: object) -> bool:
        if __o.__class__ == ConfItem:
            t = __o
            return self.name == t.name and self.type == t.type and self.value == t.value
        return False

    def __str__(self) -> str:
        return 'Configuration Item(name:{0}, type:{1}, value:{2:10})'.format(self.name, self.type, self.value)
