import subprocess
import threading
import time
import unittest
import sys

from utils.NewValue import NewValue
from utils.ShowStats import ShowStats

sys.path.append('../../src')

from utils.Configuration import Configuration
from utils.DataViewer import startDrawing, stopDrawing, DataViewer


class TestDataViewer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Configuration.parseConfiguration()

    def getRandomData(self, i):

        newValue = NewValue()
        # fuzzer.py, unit: second
        ShowStats.runTime = int(i * 35)
        # unit test
        ShowStats.lastNewFailUnitTest = newValue.genFloat(str(0.0))
        # system test
        ShowStats.lastNewFailSystemTest = newValue.genFloat(str(0.0))
        # unit test
        ShowStats.longgestUnitTestTime = newValue.genFloat(str(0.0))
        # unit test
        ShowStats.averageUnitTestTime = newValue.genFloat(str(0.0))
        # system test
        ShowStats.averageSystemTestTime = newValue.genFloat(str(0.0))
        # SingleMutator、StackedMutator
        ShowStats.mutationStrategy = newValue.genStringList("123")
        ShowStats.nowMutationType = newValue.genStringList("123")
        ShowStats.nowTestConfigurationName = newValue.genStringList("123")
        # unit test
        ShowStats.totalUnitTestcases = newValue.genInt(0)
        # system test
        ShowStats.totalSystemTestcases = newValue.genInt(0)
        # unit test, totalUnitTestcases/runTime
        ShowStats.unitTestExecSpeed = newValue.genFloat(str(0.0))
        # seedGenerator.py
        ShowStats.queueLength = newValue.genInt(0)
        # unit test
        ShowStats.totalUnitTestFailed = newValue.genInt(0)
        # system test
        ShowStats.totalSystemTestFailed = newValue.genInt(0)
        ShowStats.loopCounts = newValue.genInt(0)
        ShowStats.iterationCounts = newValue.genInt(0)

    def testDataViewer(self):
        ShowStats.initPlotData()
        dataViewer = DataViewer('testDataViewer')
        startDrawing(dataViewer)

        for i in range(15):
            self.getRandomData(i)
            ShowStats.writeToPlotData()
            time.sleep(1)

        stopDrawing(dataViewer)


if __name__ == '__main__':
    unittest.main()
