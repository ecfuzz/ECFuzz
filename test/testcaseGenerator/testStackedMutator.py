import unittest
import sys
import os

sys.path.append("../../src/")
from dataModel.ConfItem import ConfItem
from dataModel.Seed import Seed
from utils.UnitConstant import *
from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer

from testcaseGenerator.StackedMutator import StackedMutator


class TestStackedMutator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `StackedMutator`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'StackedMutator'")

    def testmutate(self) -> None:
        confItems = []
        for i in range(20):
            confItems.append(ConfItem(f"ci{i}", "INT", f"{i}"))
        seed = Seed(confItems)

        mutator = StackedMutator()

        testcase = mutator.mutate(seed)

        print(seed)
        print(testcase)


if __name__ == "__main__":
    unittest.main()
