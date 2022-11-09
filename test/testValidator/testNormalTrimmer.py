import copy
import inspect
import random
import sys
import unittest

from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration

sys.path.append("../../src")

from dataModel.ConfItem import ConfItem
from testValidator.VirtualSystemTester import VirtualSystemTester
from testValidator.NormalTrimmer import NormalTrimmer
from dataModel.Testcase import Testcase


class testNormalTrimmer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()

    def testNormalTrimmer(self) -> None:
        confItemIndexes = list(range(20))
        defaultValueMap = {f"ci{i}": "ok" for i in confItemIndexes}

        random.shuffle(confItemIndexes)

        vulnerableConfItemIndexes = confItemIndexes[:5]
        vulnerableConfItems: dict[str:list[str]] = {f"ci{i}": ["notok"] for i in vulnerableConfItemIndexes}

        targetConfItemIndexes = confItemIndexes[:15]
        targetConfItems = []
        for i in targetConfItemIndexes:
            if i in vulnerableConfItemIndexes:
                targetConfItems.append(ConfItem(f"ci{i}", "str", "notok"))
            else:
                targetConfItems.append(ConfItem(f"ci{i}", "str", "ok"))
        random.shuffle(targetConfItems)
        testcase = Testcase(targetConfItems)

        systemTester = VirtualSystemTester(vulnerableConfItems)

        trimmer = NormalTrimmer(systemTester, defaultValueMap)

        print("Before Trimming:")
        print(testcase)

        testcase = trimmer.trimTestcase(copy.deepcopy(testcase))

        print("After Normal Trimming:")
        print(testcase)

    def testNormalTrimmerBig(self) -> None:
        confItemIndexes = list(range(100))
        defaultValueMap = {f"ci{i}": "ok" for i in confItemIndexes}

        random.shuffle(confItemIndexes)

        vulnerableConfItemIndexes = confItemIndexes[:5]
        vulnerableConfItems: dict[str:list[str]] = {f"ci{i}": ["notok"] for i in vulnerableConfItemIndexes}

        targetConfItemIndexes = confItemIndexes[:50]
        targetConfItems = []
        for i in targetConfItemIndexes:
            if i in vulnerableConfItemIndexes:
                targetConfItems.append(ConfItem(f"ci{i}", "str", "notok"))
            else:
                targetConfItems.append(ConfItem(f"ci{i}", "str", "ok"))
        random.shuffle(targetConfItems)
        testcase = Testcase(targetConfItems)

        systemTester = VirtualSystemTester(vulnerableConfItems)

        trimmer = NormalTrimmer(systemTester, defaultValueMap)

        print("Before Trimming:")
        print(testcase)

        testcase = trimmer.trimTestcase(copy.deepcopy(testcase))

        print("After Normal Trimming:")
        print(testcase)


if __name__ == "__main__":
    # unittest.main()

    load = unittest.TestLoader()

    suit = load.loadTestsFromName("testNormalTrimmer")

    testModules = []

    testModules.append(suit)

    suits = unittest.TestSuite(testModules)

    run = unittest.TextTestRunner()

    run.run(suits)