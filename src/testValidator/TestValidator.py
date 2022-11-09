import importlib

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
        self.sysTester = SystemTester()
        confItems = ConfAnalyzer.confItemsBasic + ConfAnalyzer.confItemsMutable
        confItemValueMap = ConfAnalyzer.confItemValueMap
        defaultValueMap = {name: confItemValueMap[name] for name in confItems}
        trimmerClassPath = self.fuzzerConf['trimmer']
        self.trimmer = InstanceCreator.getInstance(trimmerClassPath, self.sysTester, defaultValueMap)
        self.trimmedTestcase = None
        self.logger = getLogger()

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
        ShowStats.currentJob = 'unit testing'
        utRes = self.unitTester.runTest(testcase)
        utRes.fileDir = self.fuzzerConf['unit_test_results_dir']
        self.logger.info(">>>>[TestValidator] before write result to file")
        utRes.writeToFile()
        self.logger.info(">>>>[TestValidator] after write result to file")
        if utRes.status == 0:
            return utRes, testcase

        testcase.fileDir = Configuration.fuzzerConf['unit_testcase_dir']
        testcase.writeToFile()

        ShowStats.currentJob = 'system testing'
        stRes = self.sysTester.runTest(testcase)
        stRes.fileDir = self.fuzzerConf['sys_test_results_dir']

        if stRes.status != 0 :
            stRes.writeToFile()
        return stRes, testcase

    def getTrimmedTestcase(self) -> Testcase:
        return self.trimmedTestcase
