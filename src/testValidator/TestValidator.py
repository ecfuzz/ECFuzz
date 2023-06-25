import random, time, os
from re import sub
import subprocess
from subprocess import Popen, PIPE

from dataModel.ConfItem import ConfItem
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
from utils.MongoDb import MongoDb
from utils.getCov import getCov
from testValidator.MonitorThread import MonitorThread
from queue import Queue

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
        self.useMongo = Configuration.fuzzerConf['mongodb']
        self.mongoDb = MongoDb(self.fuzzerConf['host_ip'],(int)(self.fuzzerConf['host_port'])) if self.useMongo == 'True' else None
        self.getCov = getCov()
        self.covCnt = 1
        self.covUnitData = {}
        self.covSysData = {}
        self.covStartTime = ShowStats.fuzzerStartTime
        self.startTime = ShowStats.fuzzerStartTime
        self.saveTime = ShowStats.fuzzerStartTime

    def runTest(self, testcase: Testcase, stopSoon: Queue) -> TestResult:
        """
        Starts and collects the results of a configuration fuzzing execution campaign.

        1. perform unit tests

        2. if something interesting happened during unit tests, perform system test

        3. if something interesting happened during system test, perform testcase trimming

        Args:
            testcase: a given Testcase.
            stopSoon: stopqueue from fuzzer to kill the inner thread in time.

        Returns: testResult:  testResult (TestResult): a TestResult that contains information about the running
        status and results of the whole testing.

        """
        # cur_time = time.time()
        # this method will be called mutil times
        # if cur_time - self.covStartTime > 60*15:
        #     # it means we need to get coverage now
        #     if Configuration.fuzzerConf['project'] == 'hadoop-common':
        #         cov1 = self.getCov.get_cov_unit_hcommon()
        #         cov2 = self.getCov.get_cov_sys_hcommon()
        #         cur_index = int((cur_time - self.startTime) / 60)
        #         cur_index = str(cur_index)
        #         self.covUnitData[cur_index] = cov1
        #         self.covSysData[cur_index] = cov2
        #     elif Configuration.fuzzerConf['project'] == 'hadoop-hdfs':
        #         cov1 = self.getCov.get_cov_unit_hdfs()
        #         cov2 = self.getCov.get_cov_sys_hdfs()
        #         cur_index = int((cur_time - self.startTime) / 60)
        #         cur_index = str(cur_index)
        #         self.covUnitData[cur_index] = cov1
        #         self.covSysData[cur_index] = cov2
        #     elif Configuration.fuzzerConf['project'] == 'hbase':
        #         cov1 = self.getCov.get_cov_unit_hbase()
        #         cov2 = self.getCov.get_cov_sys_hbase()
        #         cur_index = int((cur_time - self.startTime) / 60)
        #         cur_index = str(cur_index)
        #         self.covUnitData[cur_index] = cov1
        #         self.covSysData[cur_index] = cov2
        #     elif Configuration.fuzzerConf['project'] == 'alluxio':
        #         cov1 = self.getCov.get_cov_unit_alluxio()
        #         cov2 = self.getCov.get_cov_sys_alluxio()
        #         cur_index = int((cur_time - self.startTime) / 60)
        #         cur_index = str(cur_index)
        #         self.covUnitData[cur_index] = cov1
        #         self.covSysData[cur_index] = cov2
        #     elif Configuration.fuzzerConf['project'] == 'zookeeper':
        #         cov1 = self.getCov.get_cov_unit_zookeeper()
        #         cov2 = self.getCov.get_cov_sys_zookeeper()
        #         cur_index = int((cur_time - self.startTime) / 60)
        #         cur_index = str(cur_index)
        #         self.covUnitData[cur_index] = cov1
        #         self.covSysData[cur_index] = cov2
        #     self.covStartTime = cur_time
        
        # here to save cov data, each 2h
        # save_t = time.time()
        # if save_t - self.saveTime > 60 * 2 * 60:
        #     self.insert_data(self.covUnitData, self.covSysData)
        #     self.saveTime = save_t
        
        # self.logger.info(f'>>>>[TestValidator] this time unit-cov is : {self.covUnitData}; sys-cov is : {self.covSysData}')
        
        if Configuration.fuzzerConf['project'] == 'hadoop-common':
            # add fs.defaultFS=hdfs://127.0.0.1:9000
            conf = ConfItem('fs.defaultFS','PORT','hdfs://127.0.0.1:9000')
            if  not testcase.__contains__(conf):
                testcase.addConfItem(ConfItem('fs.defaultFS','PORT','hdfs://127.0.0.1:9000'))

        if Configuration.fuzzerConf['project'] == 'hbase':
            # add hbase.rootdir=/home/hadoop/hbase-2.2.2-work/hbase-tmp
            conf = ConfItem('hbase.rootdir','DIRPATH','/home/hadoop/hbase-2.2.2-work/hbase-tmp')
            if  not testcase.__contains__(conf):
                testcase.addConfItem(ConfItem('hbase.rootdir','DIRPATH','/home/hadoop/hbase-2.2.2-work/hbase-tmp'))
        
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
            if utRes.status == 0 and self.unitTester.isNoMappingTests == False:
                # add if there is no mapping tests for testcase, then go to system test
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
            os._exit(1)
            # exit(1)
        
        # before the system run, write seed to mongodb if pro is alluxio
        if Configuration.fuzzerConf['project'] == 'alluxio':
            new_seed_data = {}
            for item in testcase.confItemList:
                new_seed_data[item.name] = item.value
            # write to db
            if self.useMongo == 'True':
                self.mongoDb.insert_map_to_db("newEastSeed", new_seed_data)
        stRes = self.sysTester.runTest(testcase, stopSoon)
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
                # self.mongoDb.insert_seed_file_to_db(testcase.filePath)
                ShowStats.lastError23 = thisTime - self.preFindTime
            elif stRes.sysFailType == 2:
                testcase.writeToFile(fileDir=Configuration.fuzzerConf['sys_testcase_fail2_dir'])
                # self.mongoDb.insert_seed_file_to_db(testcase.filePath)
                ShowStats.lastError23 = 0
                self.preFindTime = thisTime
            elif stRes.sysFailType == 3:
                testcase.writeToFile(fileDir=Configuration.fuzzerConf['sys_testcase_fail3_dir'])
                # self.mongoDb.insert_seed_file_to_db(testcase.filePath)
                ShowStats.lastError23 = 0
                self.preFindTime = thisTime
            else:
                ShowStats.lastError23 = thisTime - self.preFindTime
                self.logger.info(
                f">>>>[systest] conf_file {testcase.filePath} system test failure is cannot be classified.")          
        else:
            ShowStats.lastError23 = thisTime - self.preFindTime
            self.logger.info(f">>>>[TestValidator] {testcase.fileName} system testing succeed!")
        
        if MonitorThread.CpuException == True or MonitorThread.MemoryException == True or MonitorThread.FileSizeException == True:
            testcase.writeToFile(fileDir=Configuration.fuzzerConf['sys_testcase_other_dir'])
            if stRes.status == 1 and stRes.sysFailType == 2:
                pass
            else:
                ShowStats.totalSystemTestFailed_Type2 += 1
        
        # deal the testcase, determine whether to save it
        if MonitorThread.CpuException == True or MonitorThread.MemoryException == True or MonitorThread.FileSizeException == True or (stRes.status == 1 and  stRes.sysFailType != 1):
            expSeed = {}
            for item in testcase.confItemList:
                expSeed[item.name] = item.value
            # write to db
            if self.useMongo == 'True':
                self.mongoDb.insert_map_to_db("expSeed", expSeed)
        
        endTime = time.time()
        self.totalTime += endTime - startTime
        ShowStats.ecFuzzExecSpeed = self.testcaseNum / self.totalTime
        # self.logger.info("testvalidator-88")
        return utRes, stRes, testcase
        # return stRes, self.trimmedTestcase

    def insert_data(self, unit_data, sys_data) -> None:
        # first delete data, and then insert
        # it gurantees there is only one data in collection
        if self.useMongo == 'True':
            self.mongoDb.cov_unit_collection.delete_many({})
            self.mongoDb.insert_cov_unit_to_db(unit_data)
            self.mongoDb.cov_sys_collection.delete_many({})
            self.mongoDb.insert_cov_sys_to_db(sys_data)

    def getTrimmedTestcase(self) -> Testcase:
        return self.trimmedTestcase
