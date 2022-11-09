import operator
import subprocess
import os, time, stat
import shutil
from subprocess import PIPE, Popen, TimeoutExpired

from dataModel.Testcase import Testcase
from dataModel.TestResult import TestResult
from testValidator.Tester import Tester
from testValidator.UnitTestUtils import UnitTestUtils
from testValidator.unit_result import unit_result
from testValidator.run_unit_test_utils import run_unit_test_utils
from utils.SampleTrimmer import SampleTrimmer
from utils.TimeFilterTrimmer import TimeFilterTrimmer
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration
from utils.Logger import Logger, getLogger
from utils.ShowStats import ShowStats
from utils.UnitConstant import FUZZER_DIR

class UnitTester(Tester):
    """
    Unit Tester perform unit tests to look for possible vulnerabilities.
    """
    cur_unittest_count: int = 0
    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger()
        self.rutils = run_unit_test_utils()
        self.unitUtils = UnitTestUtils()
        self.SampleTrimmer = SampleTrimmer()
        self.TimeFilterTrimmer = TimeFilterTrimmer()
        # init pre_find_time as fuzzer start time
        self.pre_find_time: float = ShowStats.fuzzerStartTime
        self.total_time: float = 0.0 # total time for run time
        self.total_count: int = 0 # it equals to the testcases' number
        # unittest time info
        self.unitTestTimeMap = self.TimeFilterTrimmer.data

    def run_test_batch(self, param_values, associated_test_map):
        self.logger.info(f">>>>[UnitTester] start running ctests for {len(associated_test_map)} parameters")

        param_test_group = self.rutils.split_tests(associated_test_map)
        self.logger.info(f">>>>[UnitTester] splitting into {len(param_test_group)} ctest group")

        for index, group in enumerate(param_test_group):
            self.logger.info(
                f'>>>>[UnitTester] group {index}, tested_params: {",".join(group[0])}, group size: {len(group[1])}')

        start_time = time.time()
        tr = unit_result(ran_tests_and_time=set(), failed_tests=set())
        for index, group in enumerate(param_test_group):
            # do injection for different test group and chdir for testing everytime
            tested_params, tests = group
            self.unitUtils.inject_config({p: param_values[p] for p in tested_params})
            self.logger.info(
                f">>>>[UnitTester] running group {index} where {len(tested_params)} params shares {len(tests)} ctests")

            # cal the timeout
            timeout = -1
            for test in tests:
                if test in self.unitTestTimeMap:
                    timeout = max(timeout, self.unitTestTimeMap[test])
            timeout = timeout * len(tests) * 1.5 if timeout != -1 else 50 * len(tests)
            timeout = timeout + 60
            ShowStats.unitCmdTimeout = int(timeout)
            self.logger.info(f">>>>[UnitTester] timeout for grop {index} is {timeout}")
            
            test_str = self.rutils.join_test_string(tests)
            os.chdir(Configuration.putConf['testing_dir'])
            self.logger.info(f">>>>[UnitTester] chdir to {Configuration.putConf['testing_dir']}")

            cmd = self.rutils.maven_cmd(test_str)
            
            with open(os.devnull, 'w') as devnull:
                try:
                    process = subprocess.Popen(cmd, stdout=devnull, stderr=devnull, preexec_fn=os.setsid)
                    process.communicate(timeout=int(timeout))
                except TimeoutExpired as e:
                    # for test hanged
                    # process.kill()
                    os.killpg(os.getpgid(process.pid), 9)
                    self.logger.info(f">>>>[UnitTester] process killed of {e}")
                    
            os.chdir(Configuration.putConf['run_unit_dir'])
            self.logger.info(f">>>>[UnitTester] chdir to {Configuration.putConf['run_unit_dir']}")

            # print_output = self.rutils.strip_ansi(stdout.decode("ascii", "ignore"))
            # print(print_output)
            test_by_cls = self.rutils.group_test_by_cls(tests)
            for clsname, methods in test_by_cls.items():
                times, errors = self.unitUtils.parse_surefire(clsname, methods)
                for m in methods:
                    if m in times:
                        tr.ran_tests_and_time.add(f"{clsname}#{m}" + "\t" + times[m])
                        # ShowStats.longgestUnitTestTime = max(ShowStats.longgestUnitTestTime, float(times[m]))
                        # update time or add new time info
                        self.unitTestTimeMap[f"{clsname}#{m}"] = float(times[m])
                        if m in errors:
                            tr.failed_tests.add(f"{clsname}#{m}")
        duration = time.time() - start_time
        os.chdir(Configuration.putConf['run_unit_dir'])
        self.logger.info(f">>>>[UnitTester] chdir to {Configuration.putConf['run_unit_dir']}")

        self.logger.info(f">>>>[UnitTester] python-timed for running config file: {duration}")

        self.unitUtils.clean_config()
        # sort the time
        self.unitTestTimeMap = dict(sorted(self.unitTestTimeMap.items(), key=operator.itemgetter(1)))
        return tr

    def test_conf_file(self, testcase: Testcase) -> TestResult:
        self.total_count += 1
        ShowStats.totalUnitTestcases = self.total_count
        # every loop, it needs to create a new TestResult
        unit_start_time = time.time()
        unitResult = TestResult()
        test_input = self.unitUtils.extract_conf_diff(testcase)
        params = test_input.keys()
        associated_test_map, associated_tests = {}, []
        for p in params:
            if p in ConfAnalyzer.confUnitMap:
                tests = ConfAnalyzer.confUnitMap[p]
                self.logger.info(f">>>>[UnitTester] parameter {p} has {len(tests)} tests")
                associated_test_map[p] = tests
                # associated_tests = associated_tests + tests
            else:
                self.logger.info(f">>>>[UnitTester] parameter {p} has 0 tests")
        # associated_tests = set(associated_tests)
        # trim ctests
        associated_test_map = self.SampleTrimmer.trimCtests(associated_test_map)
        associated_test_map = self.TimeFilterTrimmer.trimCtests(associated_test_map, self.unitTestTimeMap)
        for conf, ts in associated_test_map.items():
            associated_tests += ts
        associated_tests = set(associated_tests)
        self.logger.info(f">>>>[UnitTester] # parameters associated with the run: {len(params)}")

        self.logger.info(f">>>>[UnitTester] # ctests to run in total: {len(associated_tests)}")

        if associated_tests:
            tr = self.run_test_batch(test_input, associated_test_map)
            ran_tests = set()
            for tup in tr.ran_tests_and_time:
                test, mvntime = tup.split("\t")
                ran_tests.add(test)
                result = "f" if test in tr.failed_tests else "p"
                # row = [test, result, str(mvntime)]
                if result == "f":
                    unitResult.status = 1
                    unitResult.failed_tests_count += 1
            self.logger.info(f">>>>[UnitTester] conf failed {len(tr.failed_tests)} ctests")

        else:
            self.logger.info(">>>>[UnitTester] no ctest failed for changed params in conf file")
            # return for test cout is zero
            return unitResult
        
        unit_end_time = time.time()
        once_unit_time = unit_end_time - unit_start_time

        self.total_time += once_unit_time
        # self.total_count += 1
        
        UnitTester.cur_unittest_count = len(associated_tests)

        ShowStats.totalRunUnitTestsCount += len(associated_tests)
        ShowStats.averageUnitTestTime = self.total_time / ShowStats.totalRunUnitTestsCount
    
        # ShowStats.totalUnitTestcases = self.total_count
        ShowStats.unitTestExecSpeed = ShowStats.totalRunUnitTestsCount / self.total_time
        # ShowStats.longgestUnitTestTime = max(ShowStats.longgestUnitTestTime, once_unit_time / len(associated_tests))
        
        if unitResult.status == 1:
            # find new failed unit tests
            ShowStats.lastNewFailUnitTest = 0.0
            self.pre_find_time = unit_end_time
            # ShowStats.totalUnitTestFailed += unitResult.failed_tests_count
        else :
            # this round don't find failed unit tests
            ShowStats.lastNewFailUnitTest = unit_end_time - self.pre_find_time
        self.logger.info("update unit run time done!!!")
        self.logger.info(">>>>[UnitTester] unit_end_time is : {}".format(unit_end_time))
        
        self.logger.info(">>>>[UnitTester]  pre_find_time is : {}".format(self.pre_find_time))
        self.logger.info(">>>>[UnitTester] ShowStats.lastNewFailUnitTest is : {}".format(ShowStats.lastNewFailUnitTest))
        return unitResult

    def runWithMutilprocess(self, testcase: Testcase) -> TestResult:
        self.total_count += 1
        ShowStats.totalUnitTestcases = self.total_count
        
        unit_start_time = time.time()
        unitResult = TestResult()
        test_input = self.unitUtils.extract_conf_diff(testcase)
        params = test_input.keys()
        associated_test_map, associated_tests = {}, []
        for p in params:
            if p in ConfAnalyzer.confUnitMap:
                tests = ConfAnalyzer.confUnitMap[p]
                self.logger.info(f">>>>[UnitTester] parameter {p} has {len(tests)} tests")
                associated_test_map[p] = tests
                # associated_tests = associated_tests + tests
            else:
                self.logger.info(f">>>>[UnitTester] parameter {p} has 0 tests")
        # associated_tests = set(associated_tests)
        # trim ctests
        associated_test_map = self.SampleTrimmer.trimCtests(associated_test_map)
        associated_test_map = self.TimeFilterTrimmer.trimCtests(associated_test_map, self.unitTestTimeMap)
        for _, ts in associated_test_map.items():
            associated_tests += ts
        associated_tests = set(associated_tests)
        self.logger.info(f">>>>[UnitTester] # parameters associated with the run: {len(params)}")

        self.logger.info(f">>>>[UnitTester] # ctests to run in total: {len(associated_tests)}")
        # cal the timeout
        timeout = -1
        for test in associated_tests:
            if test in self.unitTestTimeMap:
                timeout = max(timeout, self.unitTestTimeMap[test])
        timeout = timeout * len(tests) * 1.5 if timeout != -1 else 50 * len(tests)
        timeout = timeout + 60
        ShowStats.unitCmdTimeout = int(timeout)

        if not associated_tests:
            return unitResult
        # inject key,value to file
        self.unitUtils.inject_config(test_input)
        # change to the dir
        os.chdir(Configuration.putConf['testing_dir'])
        self.logger.info(f">>>>[UnitTester] change to testing dir : {Configuration.putConf['testing_dir']}")
        # start to run
        mvn_str = ""
        if Configuration.fuzzerConf['use_surefire'] == "True":
            mvn_str = "mvn surefire:test -Dtest={}"
        else :
            mvn_str = "mvn test -Dtest={}"
        if Configuration.fuzzerConf['project'] == "alluxio":
            if Configuration.fuzzerConf['use_surefire'] == "True":
                mvn_str = "mvn license:format surefire:test -Dtest={} -DfailIfNoTests=false -Dcheckstyle.skip -Dlicense.skip -Dfindbugs.skip -Dmaven.javadoc.skip=true"
            else :
                mvn_str = "mvn license:format test -Dtest={} -DfailIfNoTests=false -Dcheckstyle.skip -Dlicense.skip -Dfindbugs.skip -Dmaven.javadoc.skip=true"
        # all_tests = list(associated_tests)
        all_tests = self.rutils.split_tests_by_cls(associated_tests)
        popen_list = []
        # self.logger.info(f">>>>[UnitTester] mvn_str is : {mvn_str}")
        self.logger.info(f">>>>[UnitTester] all tests count is : {len(all_tests)}")
        self.logger.info(">>>>[UniTester] start to run with mutil-process")
        with open(os.devnull, 'w') as devnull:
            for index in range(len(all_tests)):
                # run each test by a shell
                cur_str = mvn_str.format(all_tests[index]) # override cur_str every time
                # self.logger.info(f">>>>[UniTester] run with tests : {all_tests[index]}")
                self.logger.info(f">>>>[UniTester] mvn str is : {cur_str}")
                popen = subprocess.Popen(cur_str, shell=True, stderr=devnull, stdout=devnull)
                popen_list.append(popen)
                ShowStats.currentUnitRoundRatio = (index + 1) / len(all_tests)
                if index % 4 == 3:
                    # each time run 5 process
                    self.logger.info(">>>>[UniTester] wait for 4 process running done")
                    for popen in popen_list:
                        # wait fall each shell execute done
                        try:
                            popen.communicate(timeout=int(timeout))
                        except TimeoutExpired as e:
                            popen.kill()
                            self.logger.info(f">>>>[UnitTester] process killed of {e}")
                    popen_list = []
                    self.logger.info(">>>>[UniTester] 4 process runned done")
            # wait for the rest of process
            for popen in popen_list:
                try:
                    popen.communicate(timeout=int(timeout))
                except TimeoutExpired as e:
                    popen.kill()
                    self.logger.info(f">>>>[UnitTester] process killed of {e}")
        self.logger.info(">>>>[UniTester] run all tests done")
        self.logger.info(">>>>[UniTester] start to parse all output file")
        # parse output
        parse_out_start_time = time.time()
        tr = unit_result(ran_tests_and_time=set(), failed_tests=set())
        test_by_clas = self.rutils.group_test_by_cls(associated_tests)
        for clsname, methods in test_by_clas.items():
            times, errors = self.unitUtils.parse_surefire(clsname, methods)
            # self.logger.info(f">>>>[UnitTester] parsed {clsname} done")
            for m in methods:
                # self.logger.info(f">>>>[UnitTester] method is : {m}")
                if m in times:
                    # record every test's time and failed test
                    tr.ran_tests_and_time.add(f"{clsname}#{m}" + "\t" + times[m])
                    # ShowStats.longgestUnitTestTime = max(ShowStats.longgestUnitTestTime, float(times[m]))
                    # update time or add new time info
                    self.unitTestTimeMap[f"{clsname}#{m}"] = float(times[m])
                    if m in errors:
                        tr.failed_tests.add(f"{clsname}#{m}")
            # self.logger.info(f">>>>[UnitTester] write out of {clsname} done")
        parse_out_end_time = time.time()
        self.logger.info(f">>>>[UnitTester] this round for parse output time is : {parse_out_end_time - parse_out_start_time}")
        self.unitUtils.clean_config()
        # change to origin dir
        os.chdir(Configuration.putConf['run_unit_dir'])
        self.logger.info(f">>>>[UnitTester] change to origin dir : {Configuration.putConf['run_unit_dir']}")

        unit_end_time = time.time()
        once_unit_time = unit_end_time - unit_start_time
        # deal with result
        if len(tr.failed_tests) != 0:
            self.logger.info(f">>>>[UnitTester] failed {len(tr.failed_tests)} test")
            unitResult.status = 1
            ShowStats.lastNewFailUnitTest = 0.0
            unitResult.failed_tests_count = len(tr.failed_tests)
            self.pre_find_time = unit_end_time
        else :
            ShowStats.lastNewFailUnitTest = unit_end_time - self.pre_find_time

        self.total_time += once_unit_time
        # self.total_count += 1
        
        UnitTester.cur_unittest_count = len(associated_tests)

        ShowStats.totalRunUnitTestsCount += len(associated_tests)
        ShowStats.averageUnitTestTime = self.total_time / ShowStats.totalRunUnitTestsCount
        # ShowStats.totalUnitTestFailed += unitResult.failed_tests_count

        # ShowStats.totalUnitTestcases = self.total_count
        ShowStats.unitTestExecSpeed = ShowStats.totalRunUnitTestsCount / self.total_time
        self.logger.info(f">>>>[UnitTester] status is : {unitResult.status}; failed tests is : {unitResult.failed_tests_count}")

        self.logger.info(">>>>[UnitTester] run one round unit test with mutil-process done")
        # sort the time
        self.unitTestTimeMap = dict(sorted(self.unitTestTimeMap.items(), key=operator.itemgetter(1)))

        return unitResult

    def preKillRun(self, testcase: Testcase) -> TestResult:
        """run with pre kill if there has failed tests.

        Args:
            testcase (Testcase): _description_

        Returns:
            TestResult: _description_
        """
        self.total_count += 1
        ShowStats.totalUnitTestcases = self.total_count
        
        unit_start_time = time.time()
        unitResult = TestResult()
        test_input = self.unitUtils.extract_conf_diff(testcase)
        params = test_input.keys()
        associated_test_map, associated_tests = {}, []
        for p in params:
            if p in ConfAnalyzer.confUnitMap:
                tests = ConfAnalyzer.confUnitMap[p]
                self.logger.info(f">>>>[UnitTester] parameter {p} has {len(tests)} tests")
                associated_test_map[p] = tests
                # associated_tests = associated_tests + tests
            else:
                self.logger.info(f">>>>[UnitTester] parameter {p} has 0 tests")
        # associated_tests = set(associated_tests)
        # trim ctests
        associated_test_map = self.SampleTrimmer.trimCtests(associated_test_map)
        associated_test_map = self.TimeFilterTrimmer.trimCtests(associated_test_map, self.unitTestTimeMap)
        for _, ts in associated_test_map.items():
            associated_tests += ts
        associated_tests = set(associated_tests)
        self.logger.info(f">>>>[UnitTester] # parameters associated with the run: {len(params)}")

        self.logger.info(f">>>>[UnitTester] # ctests to run in total: {len(associated_tests)}")
        # cal the timeout
        timeout = -1
        for test in associated_tests:
            if test in self.unitTestTimeMap:
                timeout = max(timeout, self.unitTestTimeMap[test])
        timeout = timeout * len(associated_tests) * 1.5 if timeout != -1 else 50 * len(associated_tests)
        timeout = timeout + 60
        ShowStats.unitCmdTimeout = int(timeout)

        if not associated_tests:
            # return empty result
            self.logger.info(">>>>[UnitTester] no tests for cur input testcase")
            return unitResult
        # inject key,value to file
        self.unitUtils.inject_config(test_input)
        # change to the dir
        os.chdir(Configuration.putConf['testing_dir'])
        self.logger.info(f">>>>[UnitTester] change to testing dir : {Configuration.putConf['testing_dir']}")
        # start to run
        mvn_cmd =[]
        test_mode = "surefire:test" if Configuration.fuzzerConf['use_surefire'] == "True" else "test"
        maven_args = ["-DfailIfNoTests=false", "-Dcheckstyle.skip", "-Dlicense.skip", "-Dfindbugs.skip", "-Dmaven.javadoc.skip=true"] if Configuration.fuzzerConf['project'] == "alluxio" else []
        # if Configuration.fuzzerConf['project'] == "alluxio":
        #     if Configuration.fuzzerConf['use_surefire'] == "True":
        #         mvn_str = "mvn license:format surefire:test -Dtest={} -DfailIfNoTests=false -Dcheckstyle.skip -Dlicense.skip -Dfindbugs.skip -Dmaven.javadoc.skip=true"
        #     else :
        #         mvn_str = "mvn license:format test -Dtest={} -DfailIfNoTests=false -Dcheckstyle.skip -Dlicense.skip -Dfindbugs.skip -Dmaven.javadoc.skip=true"
        # all_tests = list(associated_tests)
        all_tests = self.rutils.split_tests_by_cls(associated_tests)
        # self.logger.info(f">>>>[UnitTester] mvn_str is : {mvn_str}")
        test_str = self.rutils.cal_strs(all_tests)
        
        if Configuration.fuzzerConf['project'] == "alluxio":
            mvn_cmd = ["mvn", "license:format" ,test_mode, "-Dtest={}".format(test_str)] + maven_args
        else:
            mvn_cmd = ["mvn" ,test_mode, "-Dtest={}".format(test_str)] + maven_args
        
        # mvn_str = mvn_str.format(test_str)
        self.logger.info(">>>>[UnitTester] start to run by pre kill")
        outfile = os.path.join(FUZZER_DIR,"unitResult.txt")
        # mvn_cmd[-1] = mvn_cmd[-1] + f" > {outfile} 2>&1"
        # mvn_cmd = mvn_cmd + [">",f"{outfile}","2>&1"]
        # mvn_str = mvn_str + " " + f"> {outfile} 2>&1"
        self.logger.info(f">>>>[UnitTester] mvn cmd is : {mvn_cmd}")
        cur_total_unit_test = 0
        
        # with open(os.devnull, 'w') as devnull:
        # each run will cover the old data
        # process = subprocess.Popen(mvn_str, shell=True, stdout=devnull, stderr=devnull)
        outfd = open(outfile, "w")
        process = subprocess.Popen(mvn_cmd, stderr=outfd, stdout=outfd, preexec_fn=os.setsid)
        # process.communicate()
        # process.communicate(timeout=int(timeout))
        self.logger.info(">>>>[UnitTester] real start to run")
        time.sleep(2)
        total_time = int(timeout)
        self.logger.info(f">>>>[UnitTester] timeout is : {int(timeout)}")
        s_time = time.time()
        with open(outfile, "r") as file:
            while (1):
                # each sec to check the outfile
                time.sleep(0.1)
                # total_time -= 1
                if int(time.time() - s_time) >= total_time:
                    # here it's running time is over timeout
                    # process.kill()
                    os.killpg(os.getpgid(process.pid), 9)
                    unitResult.status = 1
                    unitResult.description = "killed by timeout"
                    cur_total_unit_test += 1
                    self.logger.info(">>>>[UnitTester] kill process by timeout")
                    break
                line_info = file.readline()
                # self.logger.info(f">>>>[UnitTester] line info is : {line_info}")
                if line_info:
                    # self.logger.info(f">>>>[UnitTester] line info is : {line_info}")
                    # deal the line info : str
                    round_count, is_failed = self.rutils.deal_line_info(line_info=line_info)
                    if is_failed:
                        # process.kill()
                        os.killpg(os.getpgid(process.pid), 9)
                        unitResult.status = 1
                        unitResult.description = "killed by pre"
                        cur_total_unit_test += round_count
                        self.logger.info(">>>>[UnitTester] kill process by pre")
                        break
                    else:
                        # no falied 
                        cur_total_unit_test += round_count
                        pass
                else :
                    # no info, determine whether process is done
                    code = process.poll()
                    if code == 0:
                        # normally terminate
                        unitResult.status = 0
                        unitResult.description = "normally terminate"
                        self.logger.info(">>>>[UnitTester] process normally terminated")
                        break
                    elif code == None:
                        # running
                        continue
                    elif code == 137:
                        # killed by -9, it needs to break
                        unitResult.status = 1
                        unitResult.description = "killed by -9"
                        self.logger.info(">>>>[UnitTester] process has be killed by -9")
                        break
                    else:
                        continue
                    
        self.logger.info(f">>>>[UnitTester] this testcase's unittests count is : {cur_total_unit_test}")
        self.logger.info(">>>>[UnitTester] run by pre kill done")               
        self.unitUtils.clean_config()
        outfd.close()
        # change to origin dir
        os.chdir(Configuration.putConf['run_unit_dir'])
        self.logger.info(f">>>>[UnitTester] change to origin dir : {Configuration.putConf['run_unit_dir']}")
        
        UnitTester.cur_unittest_count = cur_total_unit_test

        unit_end_time = time.time()
        once_unit_time = unit_end_time - unit_start_time
        # deal with result
        if unitResult.status == 1:
            ShowStats.lastNewFailUnitTest = 0.0
            self.pre_find_time = unit_end_time
        else :
            ShowStats.lastNewFailUnitTest = unit_end_time - self.pre_find_time

        self.total_time += once_unit_time
        # self.total_count += 1

        ShowStats.totalRunUnitTestsCount += cur_total_unit_test
        ShowStats.averageUnitTestTime = self.total_time / ShowStats.totalRunUnitTestsCount
        # ShowStats.totalUnitTestFailed += unitResult.failed_tests_count

        # ShowStats.totalUnitTestcases = self.total_count
        ShowStats.unitTestExecSpeed = ShowStats.totalRunUnitTestsCount / self.total_time
        self.logger.info(f">>>>[UnitTester] status is : {unitResult.status}")
        # sort the time
        # self.unitTestTimeMap = dict(sorted(self.unitTestTimeMap.items(), key=operator.itemgetter(1)))

        return unitResult

    def runTest(self, testcase: Testcase) -> TestResult:
        """run the mutated conf, it will just run the diff conf

        Args:
            testcase (Testcase): _description_

        Returns:
            TestResult: _description_
        """
        # when running a new testcase, it should create a new UnitTester instance to reset it's attribute
        # rewrite runTest
        surefire_reports = Configuration.putConf['surefire_location']
        # clean the surefire-reports
        for surefire_dir in surefire_reports:
            if os.path.exists(surefire_dir):
                self.logger.info(">>>>[UnitTester] start to delete the file")
                if not os.access(surefire_dir, os.W_OK):
                    os.chmod(surefire_dir, stat.S_IWRITE)
                shutil.rmtree(surefire_dir, ignore_errors=True)
                
        if Configuration.fuzzerConf["use_pre_kill"] == 'True':
            return self.preKillRun(testcase=testcase)
        if Configuration.fuzzerConf['use_mutil_pro'] == 'True':
            return self.runWithMutilprocess(testcase)
        
        return self.test_conf_file(testcase=testcase)
        
