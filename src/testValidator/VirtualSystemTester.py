import sys
from typing import Dict, List

from dataModel.TestResult import TestResult
from dataModel.Testcase import Testcase
from testValidator.SystemTester import SystemTester


class VirtualSystemTester(SystemTester):
    """
   

    Args:
        self.vulnerableConfItems (dict{ConfItem:list[str]}):
    """

    def __init__(self, vulnerableConfItems: Dict[str, List[str]] = None):
        super(VirtualSystemTester, self).__init__()
        self.vulnerableConfItems: Dict = vulnerableConfItems

    def runTest(self, testcase: Testcase) -> TestResult:
        if self.vulnerableConfItems is None:
            print("Vulnerable Configuration Items not set!")
            return TestResult(0, "Vulnerable Configuration Items not set!")

        confItems = testcase.confItemList
        confItemMaps = {confItem.name: confItem.value for confItem in confItems}

        for key, valueList in self.vulnerableConfItems.items():
            if confItemMaps[key] not in valueList:
                return TestResult(0, "Virtual Testing Succeed.")

        return TestResult(1, "Virtual Testing Failed.")
