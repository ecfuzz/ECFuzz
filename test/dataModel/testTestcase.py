import os
import unittest

from dataModel.Testcase import Testcase
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration


class TestTestcase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()

    def test__str__(self):
        testcase = Testcase()

        print(testcase.__str__())

    def testDirectoryNotExists(self):
        testcase = Testcase()
        testcase.fileDir = 'test'
        testcase.writeToFile("test")
        os.remove(testcase.filePath)
        os.removedirs('test')

    def testZooKeeper(self):
        Configuration.fuzzerConf['project'] = 'zookeeper'
        testcase = Testcase()
        testcase.fileDir = '.'
        testcase.writeToFile("test")
        os.remove('./test.cfg')

    def testAlluxio(self):
        Configuration.fuzzerConf['project'] = 'alluxio'
        testcase = Testcase()
        testcase.fileDir = '.'
        testcase.writeToFile("test")
        os.remove('./test.properties')

    def testOther(self):
        Configuration.fuzzerConf['project'] = 'other'
        testcase = Testcase()
        testcase.fileDir = '.'
        testcase.writeToFile("test")


if __name__ == '__main__':
    unittest.main()
