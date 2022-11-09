import os
import subprocess
import time
from threading import Thread
from copy import deepcopy
from utils.UnitConstant import SRC_DIR

TESTCASES = {}


class Observer(object):
    file_index = -1
    crash_observer = None
    hang_observer = None
    termination_observer = None
    crash = False
    hang = False
    termination = False

    def __init__(self, test_cases):
        self.crash_observer = CrashObserver()
        self.crash_observer.setDaemon(True)
        self.hang_observer = HangObserver()
        self.hang_observer.setDaemon(True)
        self.termination_observer = TerminationObserver()
        self.termination_observer.setDaemon(True)

        global TESTCASES
        for i in range(test_cases.__len__()):
            id = str(i + 1)
            for testCase in test_cases:
                if testCase.id == id:
                    TESTCASES[id] = testCase

    def get_event(self, event):
        self.crash_observer.get_event(event)
        self.hang_observer.get_event(event)
        self.termination_observer.get_event(event)

    def start_crash_observer(self):
        try:
            self.crash_observer.start()
        except Exception as e:
            pass

    def start_hang_observer(self):
        try:
            self.hang_observer.start()
        except Exception as e:
            pass

    def start_termination_observer(self):
        try:
            self.termination_observer.start()
        except Exception as e:
            pass

    def stop_crash_observer(self):
        return self.crash_observer.stop()

    def stop_hang_observer(self):
        return self.hang_observer.stop()

    def stop_termination_observer(self):
        return self.termination_observer.stop()


class CrashObserver(Thread):
    event = None
    running = False
    detailed_results = {}
    result = False
    finished = False

    def __init__(self):
        Thread.__init__(self)
        self.event = None
        # /ceitinspector-code/examples/Nginx/
        subprocess.Popen(
            "bash " + os.path.join(SRC_DIR, 'testValidator',
                                   'ceit', 'system_tester',
                                   'shell', 'coredumpSetting.sh'),
            shell=True)
        # exit(0)

    def run(self):
        self.running = True
        self.finished = False
        while True:
            if self.running == True:
                self.result = False
                if self.event:
                    test_case_id = self.event
                    test_case = TESTCASES[test_case_id]
                    script = test_case.script
                    oracle_dict = test_case.oracle_dict
                    running = oracle_dict["running"]

                    if running == True:
                        pass
                    else:
                        if self.check_crash():
                            # find crash
                            self.result = True
                        else:
                            self.result = False
                    result = self.result
                    self.detailed_results[test_case_id] = result
                    self.event = None
                    if test_case_id == str(TESTCASES.__len__()):
                        self.finished = True
                        self.running = False
            else:
                break

    def check_crash(self):
        for root, dir, file in os.walk("/corefile/"):
            if file != []:
                return True
            else:
                return False

    def stop(self):
        while True:
            time.sleep(0.1)
            if self.finished:
                detailed_results = deepcopy(self.detailed_results)
                return detailed_results

    def get_event(self, event):
        while True:
            if self.event == None:
                self.event = event
                break


class HangObserver(Thread):
    event = None
    result = False
    running = False
    finished = False
    detailed_results = {}

    def __init__(self):
        Thread.__init__(self)
        self.event = None

    def run(self):
        self.running = True
        self.finished = False
        while True:
            if self.running == True:
                self.result = False
                if self.event:
                    test_case_id = self.event
                    test_case = TESTCASES[test_case_id]
                    script = test_case.script
                    oracle_dict = test_case.oracle_dict
                    running = oracle_dict["running"]

                    if running == True:
                        pass
                    else:
                        if self.check_script_running(script):
                            # find Hang
                            self.result = True
                            self.terminate_script(script)
                        else:
                            self.result = False
                    result = self.result
                    self.detailed_results[test_case_id] = result
                    self.event = None
                    if test_case_id == str(TESTCASES.__len__()):
                        self.finished = True
                        self.running = False
            else:
                break

    def terminate_script(self, script):

        os.popen('ps -ef | grep "' + script + '" | grep -v grep | awk ' + "'{print $2}' | xargs kill -9")

    def check_script_running(self, script):
        output = os.popen('ps -ef | grep "' + script + '"')
        lines = output.readlines()
        for line in lines:
            if "grep" not in line:
                return True
            else:
                return False

    def stop(self):
        while True:
            time.sleep(0.1)
            if self.finished:
                detailed_results = deepcopy(self.detailed_results)
                return detailed_results

    def get_event(self, event):
        while True:
            if self.event == None:
                self.event = event
                break


class TerminationObserver(Thread):
    event = None
    result = False
    running = False
    finished = False
    detailed_results = {}

    def __init__(self):
        Thread.__init__(self)
        self.event = None

    def run(self):
        self.running = True
        self.finished = False
        while True:
            if self.running == True:
                self.result = False
                if self.event:
                    test_case_id = self.event
                    test_case = TESTCASES[test_case_id]
                    script = test_case.script
                    oracle_dict = test_case.oracle_dict
                    running = oracle_dict["running"]
                    if running == False:
                        pass
                    else:
                        if self.check_script_running(script):
                            self.result = False
                        else:
                            # find Termination
                            self.result = True
                    result = self.result
                    self.detailed_results[test_case_id] = result
                    self.event = None
                    if test_case_id == str(TESTCASES.__len__()):
                        self.finished = True
                        self.running = False
            else:
                break

    def check_script_running(self, script):
        output = os.popen('ps -ef | grep "' + script + '"')
        lines = output.readlines()
        for line in lines:
            if "grep" not in line:
                return True
            else:
                return False

    def stop(self):
        while True:
            time.sleep(0.1)
            if self.finished:
                detailed_results = deepcopy(self.detailed_results)
                return detailed_results

    def get_event(self, event):
        while True:
            if self.event == None:
                self.event = event
                break


class EventListener(Thread):
    observer_event_queue = []
    daemon_event_queue = []
    observer = None
    running = False

    def __init__(self):
        Thread.__init__(self)

    def listen(self):
        self.running = True
        while True:
            if self.running == True:
                if self.observer_event_queue:
                    event = self.observer_event_queue.pop()
                    self.observer.get_event(event)
                if self.daemon_event_queue:
                    event = self.daemon_event_queue.pop()
                    self.daemon_process.get_event(event)
            else:
                break

    def run(self):
        try:
            self.listen()
        except Exception as e:
            print(e)

    def push_observer_event(self, string):
        self.observer_event_queue.append(string)

    def push_daemon_event(self, string):
        self.daemon_event_queue.append(string)

    def bind_observer(self, observer):
        self.observer = observer

    def bind_daemon(self, daemon):
        self.daemon_process = daemon

    def unbind(self):

        # self.observer = None
        self.running = False

    def is_running(self):
        if self.running == True:
            return True
        else:
            return False


def main():
    ob = Observer()
    ob.start_hang_observer()
    el = EventListener()
    el.bind_observer(ob)
    el.start()
    while True:
        time.sleep(2)
        el.push_observer_event("helloworld")


if __name__ == "__main__":
    main()
