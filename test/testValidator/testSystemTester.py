import os.path
import sys
import time
import unittest

sys.path.append("../../src")

from testValidator.SystemTester import SystemTester
from dataModel.Testcase import Testcase
from dataModel.TestResult import TestResult
from utils.Configuration import Configuration
from utils.ShowStats import ShowStats

class TestST(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls) -> None:
    #     warnings.simplefilter('ignore', ResourceWarning)
    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `SystemTester`")
        Configuration.parseConfiguration()
        ShowStats.fuzzerStartTime = time.time()
        ShowStats.runTime = 99999.99

    def test_runTest(self) -> TestResult:
        testcase = Testcase()
        curDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        testcase.filePath = os.path.join(curDir, Configuration.putConf['test_st_conf_path'])
        print(f"testcase file path is : {testcase.filePath}")
        return SystemTester().runTest(testcase=testcase)

if __name__ == "__main__":
    unittest.main()