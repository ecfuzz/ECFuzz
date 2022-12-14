import time

from reprint import output

from utils.Configuration import Configuration


# import curses
class ShowStats(object):
    # fuzzer start time
    fuzzerStartTime: float = 0.0
    #fuzzer.py, unit: second
    runTime: float = 0.0
    #unit test
    lastNewFailUnitTest: float = 0.0
    #system test
    lastNewFailSystemTest: float = 0.0
    #unit test
    # longgestUnitTestTime: float = 0.0
    #sys test
    longgestSystemTestTime: float = 0.0
    #unit test
    averageUnitTestTime: float = 0.0
    #system test
    averageSystemTestTime: float = 0.0
    
    mutationStrategy: str = ""
    nowMutationType: str = ""
    nowTestConfigurationName: str = ""
    #unit test
    totalUnitTestcases: int = 0
    # total unit tests hava runned
    totalRunUnitTestsCount : int = 0
    #system test
    totalSystemTestcases: int = 0
    #unit test, totalUnitTestcases/unitTestRunTime
    unitTestExecSpeed: float = 0.0
    # current unittest cmd timeout
    unitCmdTimeout: int = 0
    # current unittest round ratio
    # currentUnitRoundRatio: float = 0.0
    #system test, totalSysTestcases/systemTestRunTime
    systemTestExecSpeed: float = 0.0
    ecFuzzExecSpeed: float = 0.0

    #seedGenerator.py
    queueLength: int = 0
    #unit test
    # totalUnitTestFailed: int = 0
    #system test
    totalSystemTestFailed: int = 0
    totalSystemTestFailed_Type1: int = 0
    totalSystemTestFailed_Type2: int = 0
    totalSystemTestFailed_Type3: int = 0
    # totalSystemTestReaction_4: int = 0
    # totalAbnormalObservation: int = 0
    #fuzzer.py
    loopCounts: int = 0
    iterationCounts: int = 0

    #SeedGenerator.py, TestcaseGenerator.py, TestValidator.py
    currentJob: str = 'init...'
    
    #
    lastError23 : float = 0.0 
    stackMutationFlag : int = 0
    
    @staticmethod
    def initPlotData():
        plotDataPath = Configuration.fuzzerConf['plot_data_path']
        with open(plotDataPath, 'w') as f:
            f.write("time, loop_counts, iteration_counts, "
                    "unit_testcase_cnt, unit_ctests_cnt ,system_test_cnt, system_test_failures, "
                    "total system test failed1, total system test failed2, "
                    "total system test failed3, "
                    "longest system test time, average unit test time, average system test time, "
                    "total unit test cases, total run unit test count, "
                    "total system test cases, unit test cmd timeout, "
                    "unit test exec speed, system test exec speed, "
                    "ecFuzz exec speed, "
                    "queue length, total system test failed"
                    "\n"
                    )


    @staticmethod
    def writeToPlotData():
        plotDataPath = Configuration.fuzzerConf['plot_data_path']
        with open(plotDataPath, 'a+') as f:
            f.write(f"{int(ShowStats.runTime)}, "
                    f"{ShowStats.loopCounts}, "
                    f"{ShowStats.iterationCounts}, "
                    f"{ShowStats.totalUnitTestcases}, "
                    f"{ShowStats.totalRunUnitTestsCount}, "
                    f"{ShowStats.totalSystemTestcases}, "
                    f"{ShowStats.totalSystemTestFailed},"
                    f"{ShowStats.totalSystemTestFailed_Type1}, "
                    f"{ShowStats.totalSystemTestFailed_Type2}, "
                    f"{ShowStats.totalSystemTestFailed_Type3}, "
                    f"{ShowStats.longgestSystemTestTime}, "
                    f"{ShowStats.averageUnitTestTime}, "
                    f"{ShowStats.averageSystemTestTime}, "
                    f"{ShowStats.totalUnitTestcases}, "
                    f"{ShowStats.totalRunUnitTestsCount}, "
                    f"{ShowStats.totalSystemTestcases}, "
                    f"{ShowStats.unitCmdTimeout}, "
                    f"{ShowStats.unitTestExecSpeed}, "
                    f"{ShowStats.systemTestExecSpeed}, "
                    f"{ShowStats.ecFuzzExecSpeed}, "
                    f"{ShowStats.queueLength}, "
                    f"{ShowStats.totalSystemTestFailed}"
                    "\n"
                    )


    @staticmethod
    def getTime(seconds: int):

        # def _days(day):
        #     return "{} days, ".format(day) if day > 1 else "{} day, ".format(day)
        # def _hours(hour):  
        #     return "{} hours, ".format(hour) if hour > 1 else "{} hour, ".format(hour)
        # def _minutes(minute):
        #     return "{} minutes and ".format(minute) if minute > 1 else "{} minute and ".format(minute)
        # def _seconds(second):  
        #     return "{} seconds".format(second) if second > 1 else "{} second".format(second)

        days = str(seconds // (3600 * 24))
        hours = str((seconds // 3600) % 24)
        minutes = str((seconds // 60) % 60)
        sec = str(seconds - int(days) * (3600 * 24) - int(hours) * 3600 - int(minutes) * 60)
        return f"{days:2s} days, {hours:2s} hrs, {minutes:2s} min, {sec:2s} sec"
        # if days > 0 :
        #     return _days(days)+_hours(hours)+_minutes(minutes)+_seconds(seconds)
        # if hours > 0 :
        #     return _hours(hours)+_minutes(minutes)+_seconds(seconds)
        # if minutes > 0 :
        #     return _minutes(minutes)+_seconds(seconds)
        # return _seconds(seconds)

    @staticmethod
    def run(stopSoon) -> None:
        # curses.initscr()
        # curses.curs_set(0)
        
        # print("\33[2J")
        
        print("\33[?25l ")
        with output(initial_len=26, interval=0) as output_lines:
            while True:
                output_lines[0]  = f"\033[33m          effective configuration fuzzing (\033[32m{Configuration.fuzzerConf['project']})           "
                output_lines[1]  = f"\033[34m-------------------------------Time--------------------------------"
                output_lines[2]  = f"\033[36m                         run time: \033[37m{ShowStats.getTime(round(ShowStats.runTime))}"
                output_lines[3]  = f"\033[36m          last new fail unit test: \033[37m{ShowStats.getTime(round(ShowStats.lastNewFailUnitTest))}"
                output_lines[4]  = f"\033[36m        last new fail system test: \033[37m{ShowStats.getTime(round(ShowStats.lastNewFailSystemTest))}"
                output_lines[5]  = f"\033[36m         longest system test time: \033[37m{ShowStats.getTime(round(ShowStats.longgestSystemTestTime))}"
                output_lines[6]  = f"\033[36m           average unit test time: \033[37m{ShowStats.getTime(round(ShowStats.averageUnitTestTime))}"
                output_lines[7]  = f"\033[36m         average system test time: \033[37m{ShowStats.getTime(round(ShowStats.averageSystemTestTime))}"
                output_lines[8]  = f"\033[34m-----------------------------Mutation------------------------------"
                output_lines[9]  = f"\033[36m                mutation strategy: \033[37m{ShowStats.mutationStrategy}"
                output_lines[10] = f"\033[36m                now mutation type: \033[37m{ShowStats.nowMutationType}"
                output_lines[11] = f"\033[36m           now test configuration: \033[37m{ShowStats.nowTestConfigurationName}"
                output_lines[12] = f"\033[36m            total unit test cases: \033[37m{ShowStats.totalUnitTestcases}"
                output_lines[13] = f"\033[36m        total run unit test count: \033[37m{ShowStats.totalRunUnitTestsCount}"
                output_lines[14] = f"\033[36m          total system test cases: \033[37m{ShowStats.totalSystemTestcases}"
                output_lines[15] = f"\033[36m            unit test cmd timeout: \033[37m{ShowStats.unitCmdTimeout}sec"
                output_lines[16] = f"\033[36m             unit test exec speed: \033[37m{ShowStats.unitTestExecSpeed}/sec"
                output_lines[17] = f"\033[36m           system test exec speed: \033[37m{ShowStats.systemTestExecSpeed}/sec"
                output_lines[18] = f"\033[36m                ecFuzz exec speed: \033[37m{ShowStats.ecFuzzExecSpeed}/sec"
                output_lines[19] = f"\033[34m-------------------------Overall results---------------------------"
                output_lines[20] = f"\033[36m                 fuzzing progress: \033[37m{ShowStats.loopCounts}:{ShowStats.iterationCounts}({ShowStats.currentJob})"
                output_lines[21] = f"\033[36m                     queue length: \033[37m{ShowStats.queueLength}"
                output_lines[22] = f"\033[36m         total system test failed: \033[37m{ShowStats.totalSystemTestFailed} ({ShowStats.totalSystemTestFailed_Type1}, {ShowStats.totalSystemTestFailed_Type2}, {ShowStats.totalSystemTestFailed_Type3})"
                output_lines[23] = f"\033[34m------------------------------End----------------------------------"
                output_lines[24] = " "
                if not stopSoon.empty():
                    output_lines[25] = f"\033[32m Have a good day!"
                    print("\033[37m")
                    
                    print("\33[?25h")
                    break
                time.sleep(1)
                ShowStats.runTime = time.time() - ShowStats.fuzzerStartTime
            # print("         fast configuration fuzzing (", Configuration.fuzzerConf['project'],")           ")
            # print("-------------------------------Time--------------------------------")
            # print("run time:", ShowStats.getTime(ShowStats.runTime))
            # print("last new fail unit test:", ShowStats.getTime(ShowStats.lastNewFailUnitTest))
            # print("last new fail system test:", ShowStats.getTime(ShowStats.lastNewFailSystemTest))
            # print("longest unit test time:", ShowStats.getTime(ShowStats.longgestUnitTestTime))
            # print("average unit test time:", ShowStats.getTime(ShowStats.averageUnitTestTime))
            # print("average system test time:", ShowStats.getTime(ShowStats.averageSystemTestTime))
            # print("-----------------------------Mutation------------------------------")
            # print("mutation strategy:", ShowStats.mutationStrategy)
            # print("now mutation type:", ShowStats.nowMutationType)
            # print("now test configuration:", ShowStats.nowTestConfigurationName)
            # print("total unit test cases:", ShowStats.totalUnitTestcases)
            # print("total system test cases:", ShowStats.totalSystemTestcases)
            # print("unit test exec speed:", ShowStats.unitTestExecSpeed,"/sec")
            # print("-------------------------Overall results---------------------------")
            # print("queue length:", ShowStats.queueLength)
            # print("total unit test failed:", ShowStats.totalUnitTestFailed)
            # print("total system test failed:", ShowStats.totalSystemTestFailed)
        print("ShowStats finish.............")