import unittest
import sys


sys.path.append("../../src/")
from dataModel.ConfItem import ConfItem
from dataModel.Seed import Seed
from utils.UnitConstant import *
from testcaseGenerator.SingleMutator import SingleMutator
from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer

class TestSingleMutator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `SingleMutator`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'SingleMutator'")

    def testmutate(self) -> None:
        confItems = []
        for i in range(20):
            confItems.append(ConfItem(f"ci{i}", "INT", f"{i}"))
        seed = Seed(confItems)

        mutator = SingleMutator()

        testcase = mutator.mutate(seed)

        print(seed)
        print(testcase)


if __name__ == "__main__":
    unittest.main()
