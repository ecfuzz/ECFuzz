import json
from logging import getLogger
import os
import shutil
import stat
import sys
from copy import deepcopy
from importlib import reload

from testValidator.ceit.system_tester.observer import EventListener
from testValidator.ceit.system_tester.observer import Observer
from testValidator.ceit.system_tester.testcase import TestCase
from utils.Configuration import Configuration

INTERVAL = 0
RESULTS_PATH = ""
LOGFILE = ""


class TestEngine( object ):
    log_engine = None
    test_mode = ""
    test_cases = []
    Configuration.parseConfiguration()
    scripts = Configuration.putConf['test_scripts_path']
    oracles = Configuration.putConf['test_oracles_path']
    observer = None
    directory = ""
    reactions_matrixs = {}
    event_listener = None

    def __init__(self, log_engine, test_mode, interval, log_file_path):
        self.log_engine = log_engine
        self.log_engine.info( "TestEngine Startup." )
        self.test_mode = test_mode
        self.set_interval(interval )
        self.set_log_file_path( log_file_path )
        self.load_test_cases()
        self.logger = getLogger()

        global RESULTS_PATH
        RESULTS_PATH = Configuration.fuzzerConf['sys_test_results_dir']

    def mkdir(self):
        if os.path.exists( RESULTS_PATH ):
            if not os.access(RESULTS_PATH, os.W_OK):
                os.chmod(RESULTS_PATH, stat.S_IWRITE)
            shutil.rmtree( RESULTS_PATH )
        else:
            os.makedirs( RESULTS_PATH )

    def load_test_cases(self):
        with open( self.oracles, 'r' ) as fp1:
            with open( self.scripts, 'r' ) as fp2:
                content1 = fp1.read()
                content2 = fp2.read()
                oracle_dict = json.loads( content1 )
                script_dict = json.loads( content2 )
                length = oracle_dict.__len__()
                for i in range( length ):
                    id = i + 1
                    # print self.event_listener
                    test_case = TestCase( id=str( id ), script_dict=script_dict[str( id )],
                                          oracle_dict=oracle_dict[str( id )],
                                          interval=INTERVAL, log_file=LOGFILE, end=str( length ) )
                    self.test_cases.append( test_case )

    def set_directory(self, directory):
        directory = RESULTS_PATH + '/' + directory
        self.directory = directory
        for testcase in self.test_cases:
            testcase.set_directory( directory )
        self.logger.info("TE_set_directory:" + directory)    
        if os.path.exists( directory ):
            if not os.access(directory, os.W_OK):
                os.chmod(directory, stat.S_IWRITE)
            shutil.rmtree( directory )  
        os.makedirs( directory )

    def set_directory_offline(self, directory):
        directory = RESULTS_PATH + '/' + directory
        self.directory = directory
        for testcase in self.test_cases:
            testcase.directory = directory

    def set_interval(self, interval):
        global INTERVAL
        INTERVAL = interval

    def set_log_file_path(self, logFilePath):
        global LOGFILE
        LOGFILE = logFilePath

    def start_observer(self):
        self.observer = Observer( self.test_cases )
        self.observer.start_crash_observer()
        self.observer.start_hang_observer()
        self.observer.start_termination_observer()

        self.event_listener = EventListener()
        self.event_listener.setDaemon( True )
        self.event_listener.bind_observer( self.observer )

        for test_case in self.test_cases:
            test_case.bind( self.event_listener )

        self.event_listener.start()

    def stop_observer(self, i="", mutant={"name": "",
                                          "key": "",
                                          "operator": "",
                                          "value": ""}):
        crash = self.observer.stop_crash_observer()
        hang = self.observer.stop_hang_observer()
        termination = self.observer.stop_termination_observer()
        reactions_dict = {"Crash": crash,
                          "Hang": hang,
                          "Termination": termination}
        temp = deepcopy( reactions_dict )
        if self.reactions_matrixs.__contains__( i ):
            self.reactions_matrixs[i][mutant["name"]] = temp
        else:
            self.reactions_matrixs[i] = {}
            self.reactions_matrixs[i][mutant["name"]] = temp

        self.event_listener.unbind()
        return [crash, hang, termination]

    # def start_daemon(self, dir):
    #     from ceitinspector.modules.supporter.httpd.httpd_daemon import HttpdDaemon
    #     self.daemon = HttpdDaemon()
    #     self.daemon.set_directory(dir)
    #     self.daemon.start()
    #
    #     self.event_listener.bind_daemon( self.daemon )
    #
    #     try:
    #         self.event_listener.start()
    #     except RuntimeError:
    #         pass
    #
    #     for test_case in self.test_cases:
    #         test_case.bind( self.event_listener )

    # def stop_daemon(self):
    #     self.daemon.stop()

    def get_reactions(self, i):
        return self.reactions_matrixs[i]

    # def convert_t_files(self):
    #     from ceitinspector.modules.supporter.httpd.modperl_hacker import convert_all_t_files
    #     convert_all_t_files()