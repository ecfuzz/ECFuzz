import unittest, sys

from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration

sys.path.append("../../src")
from testValidator.VirtualSystemTester import VirtualSystemTester


class testVirtualSystemTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
    def testEmptyVulnerableConfItems(self):
        tester = VirtualSystemTester(None)
        tester.runTest(None)


if __name__ == '__main__':
    unittest.main()
