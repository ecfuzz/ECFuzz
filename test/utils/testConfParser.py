import unittest, sys, os

sys.path.append("../../src/")

from utils.ConfParser import ConfParser
from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer

class testConfParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `testConfParser`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'testConfParser'")

    def testParser(self) -> None:
        print("confItemValueMap:", ConfAnalyzer.confItemValueMap)
        print("confItemTypeMap:", ConfAnalyzer.confItemTypeMap)
if __name__ == "__main__":
    unittest.main()
