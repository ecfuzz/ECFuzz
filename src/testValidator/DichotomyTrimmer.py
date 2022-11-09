from typing import List, Tuple, Dict

from dataModel.ConfItem import ConfItem
from dataModel.Testcase import Testcase
from testValidator.NormalTrimmer import NormalTrimmer
import random

from testValidator.SystemTester import SystemTester


class DichotomyTrimmer(NormalTrimmer):
    """
   
   

    Attributes:
        threshold (int):
        maxTry (int):
    """

    def __init__(self, systemTester: SystemTester = None, defaultValueMap: Dict[str, str] = None):
        super(DichotomyTrimmer, self).__init__(systemTester, defaultValueMap)
        self.threshold = 10
        self.maxTry = 20

    def trimTestcase(self, testcase: Testcase) -> Testcase:
        confItems = testcase.confItemList
        while len(confItems) > self.threshold:
            confItems, succeed = self.dichotomySingle(confItems)
            if not succeed:
                break

        confItems = self.normalTrim(confItems)

        return Testcase(confItems)

    def dichotomySingle(self, confItems: List[ConfItem]) -> Tuple[List[ConfItem], bool]:
        """
        The dichotomySingle function takes a list of configuration items and returns a trimmed list of configuration items.
        The dichotomySingle function will try to trim the testcase by setting half of the configurations to default values,
        and run the test case. If it fails, then it will restore all original values and set another half to default values.
        This process is repeated until all configurations are set to default value, or we reach maximum try times.

        Args:
            self: Access the attributes and methods of the class in python
            confItems:List[ConfItem]: Store the configuration items that need to be trimmed

        Returns:
            trimmedConfItems : a trimmed list of configuration items
            succeed (bool) : if the dichotomy trimming succeed.
        """
        confItemsLen: int = len(confItems)

        indexes = list(range(confItemsLen))

        testcase = Testcase()

        tryCount = 0
        while True:
            random.shuffle(indexes)

            fixConfItemsIndexes = indexes[:confItemsLen//2]

            oldValueMap = {}

            # set half of configuration items to default values,
            # and store the original values.
            for i in fixConfItemsIndexes:
                confItem = confItems[i]
                oldValueMap[confItem.name] = confItem.value
                confItem.value = self.defaultValueMap[confItem.name]

            testcase.confItemList = confItems
            testcase.writeToFile('tmp_testcase')

            result = self.systemTester.runTest(testcase)

            if result.status != 0:
                trimmedConfItems = [confItems[i] for i in indexes[confItemsLen//2:]]
                return trimmedConfItems, True

            # restore the values of configuration items
            for i in fixConfItemsIndexes:
                confItem = confItems[i]
                confItem.value = oldValueMap[confItem.name]

            tryCount += 1
            if tryCount > self.maxTry:
                return confItems, False
