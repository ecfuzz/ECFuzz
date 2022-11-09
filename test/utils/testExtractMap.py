import unittest, sys, os

sys.path.append("../../src/")

from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer

class testExtractMap(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `testExtractMap`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'testExtractMap'")

    def testExtract(self) -> None:
        print("confUnitMap:", ConfAnalyzer.confUnitMap)

if __name__ == "__main__":
    unittest.main()
