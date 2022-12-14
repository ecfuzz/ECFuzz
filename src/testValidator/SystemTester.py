import os, shutil, time
import subprocess
from subprocess import Popen, PIPE, STDOUT

from dataModel.TestResult import TestResult
from dataModel.Testcase import Testcase
from testValidator.Tester import Tester
from utils.Configuration import Configuration
from utils.Logger import getLogger
from utils.ShowStats import ShowStats


class SystemTester(Tester):
    """
    System Tester perform system level testing to validate the testcase.
    """

    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger()
        self.project: str = Configuration.fuzzerConf['project']
        # self.Result = TestResult()
        # init pre_find_time as fuzzer start time
        self.preFindTime: float = ShowStats.fuzzerStartTime
        self.totalTime: float = 0.0 # total time for run time
        self.totalCount: int = 0 # it equals to the testcases' number

    def replaceConfig(self, testcase: Testcase):
        srcReplacePath = testcase.filePath
        dstReplacePath = Configuration.putConf['replace_conf_path']
        shutil.copyfile(srcReplacePath, dstReplacePath)
        self.logger.info(
            f">>>>[systest] {srcReplacePath} replacement to the corresponding configuration file:{dstReplacePath}")

    def runSystemTestUtils(self, testcase: Testcase) -> TestResult:
        Result = TestResult()
        # Result.count -= 1
        sysCmd = f"cd {Configuration.putConf['systest_shell_dir']} && {Configuration.putConf['systest_java']} {Configuration.putConf['systest_shell']}"
        self.logger.info(f">>>>[systest] {self.project} is undergoing system test validation...")
        sysStartTime = time.time()
        process = subprocess.run(sysCmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        Result.status = process.returncode
        sysEndTime = time.time()

        onceSysTime = sysEndTime - sysStartTime
        self.totalTime += onceSysTime
        self.totalCount += 1

        ShowStats.averageSystemTestTime = self.totalTime / self.totalCount
        ShowStats.systemTestExecSpeed = self.totalCount / self.totalTime
        ShowStats.totalSystemTestcases = self.totalCount
        ShowStats.longgestSystemTestTime = max(ShowStats.longgestSystemTestTime, onceSysTime)

        self.logger.info(
            f">>>>[systest] The return code of {testcase.filePath} system test verification is {Result.status}.")
        if Result.status != 0:
            ShowStats.lastNewFailSystemTest = 0.0
            self.preFindTime = sysEndTime
            # ShowStats.totalSystemTestFailed += 1
            Result.description = process.stderr
            self.logger.info(
                f">>>>[systest] conf_file {testcase.filePath} system test failure is described as {Result.description}.")
            failType1Str = "Startup phase exception"
            failType2Str = "API request Exception"
            failType3Str = "Shutdown phase exception"
            if failType1Str in Result.description:
                Result.sysFailType = 1
                ShowStats.totalSystemTestFailed_Type1 += 1
            elif failType2Str in Result.description:
                Result.sysFailType = 2
                ShowStats.totalSystemTestFailed_Type2 += 1
            elif failType3Str in Result.description:
                Result.sysFailType = 3
                ShowStats.totalSystemTestFailed_Type3 += 1
            else:
                self.logger.info(
                f">>>>[systest] conf_file {testcase.filePath} system test failure is cannot be classified.")
                Result.sysFailType = 4
            ShowStats.totalSystemTestFailed = ShowStats.totalSystemTestFailed_Type1 + ShowStats.totalSystemTestFailed_Type2 + ShowStats.totalSystemTestFailed_Type3 
        else:
            ShowStats.lastNewFailSystemTest = sysEndTime - self.preFindTime
            Result.description = "System Testing Succeed."
        return Result

    def runTest(self, testcase: Testcase) -> TestResult:
        self.replaceConfig(testcase)
        Result = self.runSystemTestUtils(testcase)
        return Result
