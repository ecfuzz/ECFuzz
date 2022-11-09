import time
import unittest
import sys
import os
import signal
sys.path.append("../../src/")

from utils.ShowStats import ShowStats
from utils.Configuration import Configuration
from utils.NewValue import NewValue
import threading
from reprint import output
from queue import Queue

stopSoon = Queue()

class TestConfAnalyzer(unittest.TestCase):

    # targetObjects = [ConfAnalyzer()]

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `ShowStats`")
        Configuration.parseConfiguration()

    @classmethod
    def getRandomData(self):
        newValue = NewValue()
        #fuzzer.py, unit: second
        ShowStats.fuzzerStartTime = 0
        ShowStats.runTime = 100000.0
        #unit test
        ShowStats.lastNewFailUnitTest = newValue.genFloat(str(0.0))
        #system test
        ShowStats.lastNewFailSystemTest = newValue.genFloat(str(0.0))
        #unit test
        ShowStats.longgestUnitTestTime = newValue.genFloat(str(0.0))
        ShowStats.longgestSystemTestTime = newValue.genFloat(str(0.0))
        #unit test
        ShowStats.averageUnitTestTime = newValue.genFloat(str(0.0))
        #system test
        ShowStats.averageSystemTestTime = newValue.genFloat(str(0.0))
        
        ShowStats.mutationStrategy = newValue.genStringList("123")
        ShowStats.nowMutationType = newValue.genStringList("123")
        ShowStats.nowTestConfigurationName = newValue.genStringList("123")
        #unit test
        ShowStats.totalUnitTestcases = newValue.genInt(0)
        ShowStats.totalRunUnitTestsCount = newValue.genInt(0)

        #system test
        ShowStats.totalSystemTestcases = newValue.genInt(0)
        #unit test, totalUnitTestcases/runTime
        ShowStats.unitTestExecSpeed = newValue.genFloat(str(0.0))
        ShowStats.systemTestExecSpeed = newValue.genFloat(str(0.0))
        #seedGenerator.py
        ShowStats.queueLength = newValue.genInt(0)
        #unit test
        ShowStats.totalUnitTestFailed = newValue.genInt(0)
        #system test 
        ShowStats.totalSystemTestFailed = newValue.genInt(0)

    @classmethod
    def sigintHandler(self, signum, frame):
        stopSoon.put(True)

    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'ShowStats'")

    def testShowStats(self) -> None:
        signal.signal(signal.SIGINT, self.sigintHandler)

        # t1 = threading.Timer(1, function=ShowStats.run, args=[output_lines])
        t1  = threading.Thread(target=ShowStats.run, args=[stopSoon])
        t1.start()
        start = time.time()
        while True:
            self.getRandomData()
            stop = time.time()
            if (stop-start) > 10:
                stopSoon.put(True)
            try:
                if (not stopSoon.empty()):
                    t1.join()
                    break
            except Exception as e:
                print(str(e))
                break
        print("\033[37m")
        
if __name__ == "__main__":
    unittest.main()
