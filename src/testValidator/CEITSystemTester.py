import os
import shutil
import time
from typing import *

from dataModel.TestResult import TestResult
from dataModel.Testcase import Testcase
from testValidator.Tester import Tester
from testValidator.ceit.TestEngine import TestEngine
from testValidator.ceit.DataEngine import DataEngine
from testValidator.ceit.ResultEngine import ResultEngine
from testValidator.ceit.data_recorder.data_structure import DetailedResults
from utils.Configuration import Configuration
from utils.Logger import getLogger
from utils.ShowStats import ShowStats


class CEITSystemTester(Tester):
    def __init__(self):
        super().__init__()
        self.logger = getLogger()
        self.project: str = Configuration.fuzzerConf['project']
        self.putConf = Configuration.putConf
        self.test_mode = self.putConf['test_mode']
        self.conf_path = self.putConf['replace_conf_path']
        self.testEngine = TestEngine(self.logger, self.test_mode,
                                     float(self.putConf['interval']), self.putConf['log_file_path'])
        self.dataEngine = DataEngine(self.logger, self.project)
        self.resultEngine = ResultEngine(self.logger, self.putConf['char2cut'])
        # init pre_find_time as fuzzer start time
        self.preFindTime: float = ShowStats.fuzzerStartTime
        self.totalTime: float = 0.0 # total time for run time
        self.totalCount: int = 0 # it equals to the testcases' number  

    def recover_conf(self):
        pass  # self.conf_engine.recoverConf()

    def transformTestcaseForCEIT(self, testcase: Testcase):
        self.option_key = 'ecfuzz'
        # testcase.fileName = testcase.generateFileName()
        self.logger.info("testcase.fileName: " + testcase.fileName)
        # self.option_key = testcase.fileName
        self.mutant_name = testcase.fileName

        # self.logger.info(f"testcase.confItemList:{testcase.confItemList}")   
        # conf_name_list = []
        # for conf_item in testcase.confItemList:
        #     conf_name_list.append(conf_item.name)
        # self.logger.info(f"conf_name_list:{conf_name_list}") 
        # conf_name_list.append(self.conf_path)
        # self.logger.info(f"filter list:{conf_name_list}")

        self.misconf = 'ecfuzz'
        self.misconf_mode = Configuration.fuzzerConf['mutator']

    def run(self) -> int:
        if self.test_mode == "Default":
            # self.testEngine.mkdir()
            self.failed_case = []
            test_cases = self.testEngine.test_cases
            self.dataEngine.set_name(self.option_key)

            self.logger.info("Testing " + " option: " + self.option_key + "  mutant name: " + self.mutant_name)
            self.testEngine.set_directory(f"{self.misconf_mode}/{self.option_key}/{self.mutant_name}")

            self.testEngine.start_observer()
            self.dataEngine.set_key(self.mutant_name)
            self.dataEngine.set_misconf(self.misconf)
            self.dataEngine.set_mutation_type(self.misconf_mode)
            self.dataEngine.set_test_case_num(test_cases.__len__())
            self.dataEngine.init_value()
            # cleancom = "rm -f `find /postgresql-11.2 -name '*.gcda' -print` & "
            # res = os.system(cleancom)
            sysStartTime = time.time()
            try:
                for test_case in test_cases:
                    self.logger.info(f"run testscript {test_case.id}")
                    test_case.run()
                    if not test_case.result:
                        self.failed_case.append(str(test_case.id))
                        self.dataEngine.set_testcase_results_fail(test_case.id)                
            except Exception as e:
                self.logger.error(f"Exception while testing: {e}")
            finally:
                self.recover_conf()
                observer_results = self.testEngine.stop_observer(self.option_key)
                self.dataEngine.set_observer_results( observer_results )
            # ceitResult.description = str(self.dataEngine.value())
            sysEndTime = time.time()
            onceSysTime = sysEndTime - sysStartTime
            self.totalTime += onceSysTime
            self.totalCount += 1
            ShowStats.averageSystemTestTime = self.totalTime / self.totalCount
            ShowStats.systemTestExecSpeed = self.totalCount / self.totalTime
            ShowStats.totalSystemTestcases = self.totalCount
            ShowStats.longgestSystemTestTime = max(ShowStats.longgestSystemTestTime, onceSysTime)
            self.logger.info(f"{self.dataEngine.value()}")
            self.dataEngine.flush()
            self.logger.info("-----------Test Report-------------")
            self.logger.info(f"There are {str(self.failed_case.__len__())} options failed to pass the tests.")

            # self.logger.info( "Details:" )
            # for i in self.failed_case:
            #     self.logger.info( "Option ID: " + i + "  Option Key: " + self.options[i]["key"] +
            #                           "  Mutant&Test Case ID: " + str( self.failed_case[i] ) )
            #     reactions = deepcopy( self.testEngine.get_reactions( i ) )
            #     self.logger.info( "Option ID: " + i + "  Mutants&Reactions: " + str( reactions ) )
            #

            self.logger.info("-----------Test Report Over-------------")
            return sysEndTime
        else:
            self.logger.error("Unrecognized test_mode!")
            return 0

    def start_offline_analyzing(self, mode="default"):
        self.failed_case = []
        test_cases = self.testEngine.test_cases

        self.dataEngine.set_name(self.option_key)

        self.logger.info("Offline Testing " + " option: " + self.option_key + " ...")

        self.testEngine.set_directory_offline(f"{self.misconf_mode}/{self.option_key}/{self.mutant_name}")
        self.dataEngine.set_key(self.mutant_name)
        self.dataEngine.set_misconf(self.misconf)
        self.dataEngine.set_mutation_type(self.misconf_mode)
        self.dataEngine.set_test_case_num(test_cases.__len__())
        self.dataEngine.init_value()
        try:
            for test_case in test_cases:
                test_case.run_offline()
                if not test_case.result:
                    self.failed_case.append(str(test_case.id))
                    self.dataEngine.set_testcase_results_fail(test_case.id)
        except Exception as e:
            self.logger.error(f"Exception while testing: {e}")
        finally:
            self.recover_conf()
        self.logger.info(f"{self.dataEngine.value()}")
        self.dataEngine.flush()
        self.logger.info("-----------Offline Test Report-------------")
        self.logger.info(f"There are {str(self.failed_case.__len__())} options failed to pass the tests.")

        # self.logger.info( "Details:" )
        # for i in self.failed_case:
        #     self.logger.info( "Option ID: " + i + "  Option Key: " + self.options[i]["key"] +
        #                           "  Mutant&Test Case ID: " + str( self.failed_case[i] ) )
        #     reactions = deepcopy( self.testEngine.get_reactions( i ) )
        #     self.logger.info( "Option ID: " + i + "  Mutants&Reactions: " + str( reactions ) )
        #
        self.logger.info("-----------Test Report Over-------------")

    def failures_analyzing(self, testcase: Testcase, mode="default"):

        self.logger.info("-----------Failures Anazlyzing: -------------")

        base_dir = self.misconf_mode

        for test_case_id in self.failed_case:
            target_dir = os.path.join(base_dir, self.option_key, self.mutant_name)
            self.resultEngine.set_directory(target_dir)
            self.resultEngine.build_indexes()

            conf_name_list = [i.name for i in testcase.confItemList]
            conf_name_list.append(self.conf_path)
            filter_list = conf_name_list
            self.logger.info(f"filter list:{filter_list}") 
            overall_results = self.resultEngine.query_with_filter(filter_list)
        
            analyzer_results = self.resultEngine.get_analyzer_results()
            self.dataEngine.set_name(self.option_key)
            self.dataEngine.set_key(self.mutant_name)
            self.dataEngine.load_value()
            self.dataEngine.set_analyzer_results(analyzer_results)
            self.dataEngine.flush()
            if overall_results:
                self.logger.info(f"Option Key: {self.option_key}  Mutant: {self.mutant_name}  Result: Good")

            else:
                self.logger.info(f"Option Key: {self.option_key}  Mutant: {self.mutant_name}  Result: Bad")

        self.logger.info("-----------Failures Anazlyzing -------------")

    def classify_overall_results(self, file_path, sysEndTime) -> Tuple[int, int, int]:
        status = 0
        ceitType = 0
        abObservation = 0
        self.logger.info("ready to dump overall results")
        # self.logger.info(f"{self.dataEngine.value()}")
        self.logger.info(f"{self.dataEngine.value.overall_results()}")
        testcase_results = self.dataEngine.value.overall_results.results["testcase_results"]
        analyzer_results = self.dataEngine.value.overall_results.results["analyzer_results"]
        if testcase_results == "Fail":
            status = 1
            ShowStats.lastNewFailSystemTest = 0.0
            self.preFindTime = sysEndTime
            ShowStats.totalSystemTestFailed += 1
        else:
            ShowStats.lastNewFailSystemTest = sysEndTime - self.preFindTime
        if testcase_results == "Pass" and analyzer_results == "Good":
            ceitType = 1
            ShowStats.totalSystemTestReaction_1 += 1
        elif testcase_results == "Fail" and analyzer_results == "Good":
            ceitType = 2
            ShowStats.totalSystemTestReaction_2 += 1
        elif testcase_results == "Fail" and analyzer_results == "Bad":
            ceitType = 3
            ShowStats.totalSystemTestReaction_3 += 1
        elif testcase_results == "Pass" and analyzer_results == "Bad":
            ceitType = 4
            ShowStats.totalSystemTestReaction_4 += 1
        observer_crash_results = str(self.dataEngine.value.overall_results.results["observer_results"]["crash"])
        observer_hang_results = str(self.dataEngine.value.overall_results.results["observer_results"]["hang"])
        observer_termination_results = str(self.dataEngine.value.overall_results.results["observer_results"]["termination"])
        if observer_crash_results == "True" or observer_hang_results == "True" or observer_termination_results == "True":
            abObservation = 1
            ShowStats.totalAbnormalObservation += 1
        # self.dataEngine.dump_overall_results(file_path)
        return status, ceitType, abObservation        
        

    def replaceConfig(self, testcase: Testcase):
        srcReplacePath = testcase.filePath
        dstReplacePath = Configuration.putConf['replace_conf_path']
        shutil.copyfile(srcReplacePath, dstReplacePath)
        self.logger.info(
            f">>>>[CEIT systest] {srcReplacePath} replacement to the corresponding configuration file:{dstReplacePath}")

    def runTest(self, testcase: Testcase) -> TestResult:
        self.replaceConfig(testcase)
        self.transformTestcaseForCEIT(testcase)
        sysEndTime = self.run()
        # self.start_offline_analyzing()
        self.failures_analyzing(testcase=testcase)
        ceitStatus, ceitType, abObservation = self.classify_overall_results(os.path.join(Configuration.fuzzerConf['sys_test_results_dir'],'ceit.csv'), sysEndTime)
        self.logger.info("ceit-run-173")
        self.logger.info(f">>>>[CEIT systest] status: {ceitStatus}, ceitType: {ceitType}, abnormalObservation: {abObservation}.")
        return TestResult(status = ceitStatus, ceitType = ceitType, abnormalObservation = abObservation, description = str(self.dataEngine.value.overall_results()))
