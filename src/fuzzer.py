import os
import shutil
import stat
import sys
from time import time
import logging
from typing import Dict
import gc

from seedGenerator.SeedGenerator import SeedGenerator
from testValidator.TestValidator import TestValidator
from testcaseGenerator.TestcaseGenerator import TestcaseGenerator
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration

from utils.InstanceCreator import InstanceCreator
from utils.Logger import Logger
from utils.ShowStats import ShowStats

import time, signal, threading

from queue import Queue

stopSoon = Queue()


class Fuzzer(object):
    def __init__(self):
        self.logger: logging.Logger = Logger.get_logger()
        self.logger.info("Initializing Fuzzer...")

        self.logger.info("Parse configurations...")
        Configuration.parseConfiguration()
        self.fuzzerConf: Dict[str, str] = Configuration.fuzzerConf
        self.putConf: Dict[str, str] = Configuration.putConf

        ShowStats.mutationStrategy = self.fuzzerConf['mutator'].split(".")[-1]
        # ShowStats.mutationStrategy = "SingleMutator"
        ShowStats.fuzzerStartTime = time.time()

        self.logger.info("Analyze PUT configurations...")
        ConfAnalyzer.analyzeConfItems()

        self.logger.info("Creating a SeedGenerator...")
        self.seedGenerator: SeedGenerator = SeedGenerator()

        self.logger.info("Creating a TestcaseGenerator...")
        mutatorClassPath = self.fuzzerConf['mutator']
        self.testcaseGenerator: TestcaseGenerator = TestcaseGenerator(InstanceCreator.getInstance(mutatorClassPath))

        self.logger.info("Creating a TestValidator...")
        self.testValidator: TestValidator = TestValidator()

        if os.path.exists(self.fuzzerConf['plot_data_path']):
            os.remove(self.fuzzerConf['plot_data_path'])

        if self.fuzzerConf['data_viewer'] == 'True':
            from utils.DataViewer import DataViewer
            self.dataViewer = DataViewer(self.fuzzerConf['data_viewer_env'])

    def sigintHandler(self, signum, frame):
        stopSoon.put(True)
        self.logger.info(f">>>>[fuzzer] receive SIGINT")
        time.sleep(1)
        exit(0)
        # process.kill()
    
    def deleteDir(self, directory):
        if os.path.exists( directory ):
            if not os.access(directory, os.W_OK):
                os.chmod(directory, stat.S_IWRITE)
            shutil.rmtree(directory) 

    def run(self):
        """
        The run function is the main function of the fuzzer. It is responsible for
        looping through all the test cases and running them against a target. The
        fuzzer will run each test case in order, one after another, until it has reached
        the end of its list, or it has reached a maximum number of loops (if specified).
        """
        if self.fuzzerConf['data_viewer'] == 'True':
            from utils.DataViewer import startDrawing
            startDrawing(self.dataViewer)

        ShowStats.initPlotData()
        ShowStats.writeToPlotData()

        signal.signal(signal.SIGINT, self.sigintHandler)
        t1 = threading.Thread(target=ShowStats.run, args=[stopSoon])
        t1.start()
        fuzzingLoop = int(self.fuzzerConf['fuzzing_loop'])

        self.deleteDir(Configuration.fuzzerConf['unit_testcase_dir'])
        self.deleteDir(Configuration.fuzzerConf['unit_test_results_dir'])
        self.deleteDir(Configuration.fuzzerConf['sys_test_results_dir'])
        self.deleteDir(Configuration.fuzzerConf['sys_testcase_fail_dir'])

        print("\033[37m")
        if fuzzingLoop > 0:
            self.logger.info(f"Fuzzer ready to run for {fuzzingLoop} loops...")
            for _ in range(fuzzingLoop):
                try:
                    if (not stopSoon.empty()):
                        t1.join()
                        break
                except Exception as e:
                    print(e)
                    break
                try:
                    self.loop()
                except Exception as e:
                    self.logger.info(e)
                    break
        else:
            self.logger.info("Fuzzer ready to run forever...")
            while True:
                try:
                    if not stopSoon.empty():
                        t1.join()
                        break
                except Exception as e:
                    print(e)
                    break
                try:
                    self.loop()
                except Exception as e:
                    self.logger.info(e)
                    break
        stopSoon.put(True)
        self.logger.info(f">>>>[fuzzer] hava a good time")
        print("\033[37m")
        if self.fuzzerConf['data_viewer'] == 'True':
            from utils.DataViewer import stopDrawing
            stopDrawing(self.dataViewer)

    def loop(self):
        """
        The loop function is the core of the fuzzer. It is meant to be run in a while loop,
        and it accomplishes the following:
            1. Generate a seed from our seed pool (see SeedPool class)
            2. Mutate this seed into multiple test cases using our TestcaseGenerator class (see TestcaseGenerator class)
            3. Run each of these test cases through our TestValidator and collect their results (see TestValidator class)

            If any result yields an interesting value, we add that seed back to our pool for future iterations.
        """
        #
        self.logger.info("Generator a Seed from SeedGenerator")
        seed = self.seedGenerator.generateSeed()
        ShowStats.queueLength = len(self.seedGenerator.seedPool)
        
        testcasePerSeed = int(self.fuzzerConf['testcase_per_seed'])
        for _ in range(testcasePerSeed):
            self.logger.info(">>>>[fuzzer] start to mutate seed")
            self.logger.info(">>>>[fuzzer] seed len is : {}".format(seed.confItemList.__len__()))
            testcase = self.testcaseGenerator.mutate(seed)
            self.logger.info(">>>>[fuzzer] mutated testcase's length is : {}".format(len(testcase.confItemList)))
            
            utResult, sysResult, trimmedTestcase = self.testValidator.runTest(testcase)
            self.logger.info(">>>>[fuzzer] testValidator done")
            # if result.status == 1:  
            #     self.seedGenerator.addSeedToPool(trimmedTestcase)
            if (utResult != None) and (utResult.status == 1) and (sysResult != None) and (sysResult.status == 0):
                self.seedGenerator.addSeedToPool(trimmedTestcase)
            self.logger.info(">>>>[fuzzer] handle seed done")
            ShowStats.writeToPlotData()
            ShowStats.iterationCounts += 1
        ShowStats.loopCounts += 1
        # if ShowStats.loopCounts % 5 == 0:
        #     # gc on each five round
        #     gc.collect()
        self.logger.info("run() loop end -150")


if __name__ == "__main__":
    fuzzer = Fuzzer()
    fuzzer.run()
