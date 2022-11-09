from abc import ABCMeta
from dataModel.WriteToFileInterface import WriteToFileInterface


class CounterWriteToFileInterface(WriteToFileInterface, metaclass=ABCMeta):
    """
    A WriteToFileInterface but with a counter to automatically generate file name.
    """

    # a counter to record how many instances have been created.
    count = 0

    def __init__(self) -> None:
        super().__init__()
        self.__class__.count += 1

    def generateFileName(self) -> str:
        return f"{self.__class__.__name__}-{str(self.__class__.count)}"
