import os, shutil, time, stat
import subprocess, threading
from subprocess import Popen, PIPE, STDOUT

from dataModel.TestResult import TestResult
from dataModel.Testcase import Testcase
from testValidator.Tester import Tester
from utils.Configuration import Configuration
from utils.Logger import getLogger
from utils.ShowStats import ShowStats
from utils.ConfAnalyzer import ConfAnalyzer
from queue import Queue
from testValidator.MonitorThread import MonitorThread
from utils.UnitConstant import DATA_DIR

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
        self.exceptionMap = {} # 
        self.exceptionMapReason = {} # 
        self.valueMap = ConfAnalyzer.confItemValueMap
        self.logLocation = {
            "hbase": os.path.join(DATA_DIR,"app_sysTest/hbase-2.2.2-work/logs"),
            "hadoop-hdfs": os.path.join(DATA_DIR, "app_sysTest/hadoop-2.8.5-work/logs"),
            "hadoop-common": os.path.join(DATA_DIR, "app_sysTest/hadoop-2.8.5-work/logs"),
            "alluxio": os.path.join(DATA_DIR, "app_sysTest/alluxio-2.1.0-work/logs"),
            "zookeeper": os.path.join(DATA_DIR, "app_sysTest/zookeeper-3.5.6-work/logs")
        }

    def replaceConfig(self, testcase: Testcase):
        srcReplacePath = testcase.filePath
        dstReplacePath = Configuration.putConf['replace_conf_path']
        shutil.copyfile(srcReplacePath, dstReplacePath)
        self.logger.info(
            f">>>>[systest] {srcReplacePath} replacement to the corresponding configuration file:{dstReplacePath}")

    def runSystemTestUtils(self, testcase: Testcase, logDir: str, stopSoon: Queue) -> TestResult:
        Result = TestResult()
        # Result.count -= 1
        # if self.project == "alluxio":
        #     sysChmod = "echo kb310 | sudo -S chmod -R 777 /home/hadoop/ecfuzz/data/app_sysTest/alluxio-2.1.0-work/underFSStorage"
        #     process = subprocess.run(sysChmod, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True) 
        sysCmd = f"cd {Configuration.putConf['systest_shell_dir']} && {Configuration.putConf['systest_java']} {Configuration.putConf['systest_shell']}"
        self.logger.info(f">>>>[systest] {self.project} is undergoing system test validation...")
        sysStartTime = time.time()
        stop = Queue()
        threading.Thread(target=MonitorThread.threadMonitor, args=[stop, logDir, stopSoon]).start()
        process = subprocess.run(sysCmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        Result.status = process.returncode
        sysEndTime = time.time()
        stop.put(1)

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
                # modify confMutaionInfo
                for confItem in testcase.confItemList:
                    if confItem.isMutated == True:
                        ConfAnalyzer.confMutationInfo[confItem.name][1] += 1
                        # # update excludeConf
                        # if confItem.name not in ConfAnalyzer.excludeConf:
                        #     num1, num2 = ConfAnalyzer.confMutationInfo[confItem.name][0], ConfAnalyzer.confMutationInfo[confItem.name][1]
                        #     if num2 >= 10 and (float(num2) / num1) > 0.75:
                        #         ConfAnalyzer.excludeConf.append(confItem.name) 
            elif failType2Str in Result.description:
                Result.sysFailType = 2
                ShowStats.totalSystemTestFailed_Type2 += 1
                expList = self.dealWithExp(Result.description)
                exp = "" if len(expList) == 0 else expList[0] if len(expList) == 1 else expList[1]
                if exp != "":
                    if exp not in self.exceptionMap:
                        self.exceptionMap[exp] = 1
                    else:
                        self.exceptionMap[exp] += 1
                if exp != "":
                    # deal with exceptionMapReason
                    # testcase of different
                    diffVal = {}
                    for conf in testcase.confItemList:
                        # if value is different from orginal value, add it to diffval
                        if conf.name in self.valueMap and conf.value != self.valueMap[conf.name]:
                            if conf.name not in diffVal:
                                diffVal[conf.name] = conf.value
                    if exp not in self.exceptionMapReason:
                        self.exceptionMapReason[exp] = []          
                    if len(diffVal) != 0:
                        self.exceptionMapReason[exp].append(diffVal)
            
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
        self.logger.info(f">>>>[systest] exceptionMap is : {self.exceptionMap}")
        self.logger.info(f">>>>[systest] exceptionmapreason is : {self.exceptionMapReason}")
        return Result
    
    def dealWithExp(self, description:str) -> str:
        exceptionFilter = "[info_excetion]"
        res = []
        try:
            index = description.find(exceptionFilter)
            left = description[index+15:]
            alters = left.split('.')
            for al in alters:
                if al.find('Exception') != -1:
                    idx = al.find('Exception')
                    tmpRes = al[:idx+9]
                    if len(al)>len(tmpRes) and al[idx+9] == '$':
                        idx1 = al[idx+9:].find('Exception')
                        if idx1 != -1:
                            tmp = al[idx+9:]
                            tmpRes += tmp[:idx1+9]
                    res.append(tmpRes)
        except Exception as e:
            self.logger.info(e)
        return res
            
    def deleteDir(self, directory):
        if os.path.exists( directory ):
            if not os.access(directory, os.W_OK):
                os.chmod(directory, stat.S_IWRITE)
            shutil.rmtree(directory) 

    def runTest(self, testcase: Testcase, stopSoon) -> TestResult:
        # if Configuration.fuzzerConf['project'] == 'hbase':
        #     self.deleteDir("/home/hadoop/ecfuzz/data/app_sysTest/hbase-2.2.2-work/logs")
        logLoc = self.logLocation[Configuration.fuzzerConf["project"]]
        self.deleteDir(logLoc)
        self.replaceConfig(testcase)
        Result = self.runSystemTestUtils(testcase, logLoc, stopSoon)
        return Result
    