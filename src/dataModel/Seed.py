from typing import List

from dataModel.ConfItem import ConfItem
from dataModel.CounterWriteToFileInterface import CounterWriteToFileInterface


class Seed(CounterWriteToFileInterface):
    """
    This is a data model for seed in configuration fuzzing.

    Attributes:
        confItemList (List[ConfItem]) :
        _noneConfItem (ConfItem):
    """

    def __init__(self, confItems: List[ConfItem] = None) -> None:
        if confItems is None:
            confItems = []
        super().__init__()
        self.confItemList: List[ConfItem] = confItems
        self._noneConfItem = ConfItem()

    def __getitem__(self, idx: int) -> ConfItem:
        if idx >= self.confItemList.__len__():
            return self._noneConfItem
        else:
            return self.confItemList[idx]

    def __setitem__(self, idx, value):
        self.confItemList[idx] = value

    def __contains__(self, confItem: ConfItem) -> bool:
        return self.confItemList.__contains__(confItem)

    def __str__(self) -> str:
        return "Seed:\n" + "".join(conf.__str__() + "\n" for conf in self.confItemList)

    def addConfItem(self, confItem: ConfItem) -> None:
        """
        The addConfItem function adds a ConfItem to the list of confItems.
        It does not check for duplicates, so it is possible to add multiple ConfItems with the same name.

        Args:
            self: Access the attributes and methods of the class
            confItem:ConfItem: Add a confitem object to the list of confitems

        Returns:
            None
        """
        if not self.__contains__(confItem):
            self.confItemList.append(confItem)
