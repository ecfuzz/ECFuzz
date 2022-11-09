import random, time
from re import sub
import subprocess
from subprocess import Popen, PIPE

from dataModel.TestResult import TestResult
from dataModel.Testcase import Testcase
from testValidator.DichotomyTrimmer import DichotomyTrimmer
from testValidator.SystemTester import SystemTester
from testValidator.UnitTester import UnitTester
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration
from utils.InstanceCreator import InstanceCreator
from utils.ShowStats import ShowStats
from utils.Logger import Logger, getLogger


class TestValidator(object):
    """
    Test Validator starts and collects the results of a configuration fuzzing execution campaign.
    """

    def __init__(self) -> None:
        self.fuzzerConf = Configuration.fuzzerConf
        self.putConf = Configuration.putConf
        self.unitTester = UnitTester()
        self.skipUnitTest = self.fuzzerConf['skip_unit_test']
        self.sysTester = InstanceCreator.getInstance(self.fuzzerConf['systemtester'])
        self.forceSystemTestingRatio = float(self.fuzzerConf['force_system_testing_ratio'])
        confItems = ConfAnalyzer.confItemsBasic + ConfAnalyzer.confItemsMutable
        confItemValueMap = ConfAnalyzer.confItemValueMap
        defaultValueMap = {name: confItemValueMap[name] for name in confItems}
        trimmerClassPath = self.fuzzerConf['trimmer']
        self.trimmer = InstanceCreator.getInstance(trimmerClassPath, self.sysTester, defaultValueMap)
        self.trimmedTestcase = None
        self.logger = getLogger()
        self.totalTime = 0
        self.testcaseNum = 0
        self.preFindTime: float = ShowStats.fuzzerStartTime
        self.twoH : int = 2 * 3600
        self.oneH : int = 1 * 3600

    def runTest(self, testcase: Testcase) -> TestResult:
        """
        Starts and collects the results of a configuration fuzzing execution campaign.

        1. perform unit tests

        2. if something interesting happened during unit tests, perform system test

        3. if something interesting happened during system test, perform testcase trimming

        Args:
            testcase: a given Testcase.

        Returns: testResult:  testResult (TestResult): a TestResult that contains information about the running
        status and results of the whole testing.

        """
        # update flag
        if ShowStats.mutationStrategy == "SmartMutator":
            if ShowStats.stackMutationFlag == 0:
                if ShowStats.lastError23 > self.twoH:
                    ShowStats.stackMutationFlag = 1
                    ShowStats.lastError23 = 0
                    if ShowStats.mutationStrategy == "SmartMutator" or ShowStats.mutationStrategy == "SmartMutator/SingleMutator":
                        ShowStats.mutationStrategy = "SmartMutator/StackedMutator"
            elif ShowStats.stackMutationFlag == 1:
                if ShowStats.lastError23 > self.oneH:
                    ShowStats.stackMutationFlag = 0
                    ShowStats.lastError23 = 0
                    if ShowStats.mutationStrategy == "SmartMutator" or ShowStats.mutationStrategy == "SmartMutator/StackedMutator":
                        ShowStats.mutationStrategy = "SmartMutator/SingleMutator"
            else:
                pass
    
        startTime = time.time()
        utRes = None
        if self.skipUnitTest == "False":
            ShowStats.currentJob = 'unit testing'
            utRes = self.unitTester.runTest(testcase)
            utRes.fileDir = self.fuzzerConf['unit_test_results_dir']
            self.logger.info(">>>>[TestValidator] before write utresult to file")
            utRes.writeToFile()
            self.logger.info(">>>>[TestValidator] after write utresult to file")
            self.testcaseNum += UnitTester.cur_unittest_count
            if utRes.status == 0:
                if random.random() > self.forceSystemTestingRatio:
                    endTime = time.time()
                    self.totalTime += endTime -startTime
                    ShowStats.ecFuzzExecSpeed = self.testcaseNum / self.totalTime
                    return utRes, None, testcase
                else:
                    self.logger.info(">>>>[TestValidator] force system testing")
        else:
            # testcase.generateFileName()
            self.logger.info(">>>>[TestValidator] skip unit test!")
        # testcase.fileDir = Configuration.fuzzerConf['unit_testcase_dir']
        testcase.writeToFile(fileDir=Configuration.fuzzerConf['unit_testcase_dir'])

        self.testcaseNum += 1

        ShowStats.currentJob = 'system testing'
        
        mvn_check = subprocess.run('ps -ef | grep maven', shell=True, stdout=subprocess.PIPE, stderr=PIPE, universal_newlines=True)
        mvn_check_len = len(mvn_check.stdout.split("\n"))
        if (mvn_check_len > 3):
            self.logger.info("maven exist!")
            exit(1)
        
        stRes = self.sysTester.runTest(testcase)
        # self.logger.info("testvalidator-73")
        stRes.fileDir = self.fuzzerConf['sys_test_results_dir']
        # self.logger.info("testvalidator-75")

        # if stRes.status != 0:
        #     ShowStats.currentJob = 'trimming'
        #     trimmedTestcase = self.trimmer.trimTestcase(testcase)
        #     trimmedTestcase.fileDir = self.fuzzerConf['seeds_dir']
        #     trimmedTestcase.writeToFile()
        #     self.trimmedTestcase = trimmedTestcase
        #     stRes.unitTestcasePath = testcase.filePath
        #     stRes.trimmedTestcasePath = trimmedTestcase.filePath
        #     stRes.writeToFile()
        thisTime = time.time()
        if stRes.status == 1:
            self.logger.info(f">>>>[TestValidator] {testcase.fileName} system testing failed with {stRes.sysFailType}")
            stRes.writeToFile()
            if stRes.sysFailType == 1:
                testcase.writeToFile(fileDir=Configuration.fuzzerConf['sys_testcase_fail1_dir'])
                ShowStats.lastError23 = thisTime - self.preFindTime
            elif stRes.sysFailType == 2:
                testcase.writeToFile(fileDir=Configuration.fuzzerConf['sys_testcase_fail2_dir'])
                ShowStats.lastError23 = 0
                self.preFindTime = thisTime
            elif stRes.sysFailType == 3:
                testcase.writeToFile(fileDir=Configuration.fuzzerConf['sys_testcase_fail3_dir'])
                ShowStats.lastError23 = 0
                self.preFindTime = thisTime
            else:
                ShowStats.lastError23 = thisTime - self.preFindTime
                self.logger.info(
                f">>>>[systest] conf_file {testcase.filePath} system test failure is cannot be classified.")          
        else:
            ShowStats.lastError23 = thisTime - self.preFindTime
            self.logger.info(f">>>>[TestValidator] {testcase.fileName} system testing succeed!")
        
        endTime = time.time()
        self.totalTime += endTime - startTime
        ShowStats.ecFuzzExecSpeed = self.testcaseNum / self.totalTime
        # self.logger.info("testvalidator-88")
        return utRes, stRes, testcase
        # return stRes, self.trimmedTestcase

    def getTrimmedTestcase(self) -> Testcase:
        return self.trimmedTestcase
