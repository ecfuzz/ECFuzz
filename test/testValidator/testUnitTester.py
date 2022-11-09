import os.path
import sys
import time
import unittest

sys.path.append("../../src")

from dataModel.ConfItem import ConfItem
from testValidator.UnitTester import UnitTester
from dataModel.Testcase import Testcase
from dataModel.TestResult import TestResult
from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer
from utils.ShowStats import ShowStats

class TestUT(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `TestUT`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()
        ShowStats.fuzzerStartTime = time.time()
        ShowStats.runTime = 99999.99

    def test_runTest(self) -> TestResult:
        conf = []
        # for hdfs
        conf.append(ConfItem("dfs.datanode.http.internal-proxy.port","INT","0"))
        # for hbase
        conf.append(ConfItem("hbase.master.info.port","INT","16010"))
        # for zookeeper
        conf.append(ConfItem("maxClientCnxns","INT","50"))
        # for alluxio
        conf.append(ConfItem("alluxio.worker.web.port","INT","30000"))
        testcase = Testcase(conf)
        return UnitTester().runTest(testcase=testcase)

if __name__ == "__main__":
    unittest.main()
    
