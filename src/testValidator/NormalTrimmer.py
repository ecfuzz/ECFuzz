from typing import List, Dict

from dataModel.ConfItem import ConfItem
from dataModel.Testcase import Testcase
from testValidator.SystemTester import SystemTester
from testValidator.Trimmer import Trimmer


class NormalTrimmer(Trimmer):
    """
   
    """

    def __init__(self, systemTester: SystemTester = None, defaultValueMap: Dict[str, str] = None):
        super(NormalTrimmer, self).__init__(systemTester, defaultValueMap)

    def trimTestcase(self, testcase: Testcase) -> Testcase:

        confItems: List[ConfItem] = self.normalTrim(testcase.confItemList)

        testcase = Testcase(confItems)

        return testcase

    def normalTrim(self, confItems: List[ConfItem]) -> List[ConfItem]:
        """
       

        Args:
            confItems: a list of configuration items needed to be trimmed

        Returns:
            trimmedConfItems : a trimmed list of configuration items
        """

        trimmedConfItems = []

        testcase = Testcase()

        for confItem in confItems:
            oldValue = confItem.value
            confItem.value = self.defaultValueMap[confItem.name]

            testcase.confItemList = confItems
            testcase.writeToFile('tmp_testcase')

            result = self.systemTester.runTest(testcase)

            confItem.value = oldValue

            if result.status == 0:
                trimmedConfItems.append(confItem)

        return trimmedConfItems
