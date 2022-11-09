import unittest
import sys
import os

sys.path.append("../../src/")

from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer

class TestConfAnalyzer(unittest.TestCase):

    # fileCreated = []

    # targetObjects = [ConfAnalyzer()]

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `ClassifyConfItems`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'ClassifyConfItems'")

    def testclassifyConfItems(self) -> None:
        print("confItemsBasic:", ConfAnalyzer.confItemsBasic)
        print("confItemsMutable:", ConfAnalyzer.confItemsMutable)

if __name__ == "__main__":
    unittest.main()
