import os, gc
import subprocess
import time
from threading import Timer

from utils.Configuration import Configuration
from utils.Logger import getLogger

class TestCase( object ):
    script_dict = {}
    oracle_dict = {}
    script = ""
    oracle = ""
    id = ""
    result = False
    directory = ""
    end = ""
    log_file = ""
    event_listener = None
    test_path = ""

    def __init__(self, id, script_dict, oracle_dict, interval, log_file, end):
        self.id = id
        self.script_dict = script_dict
        self.oracle_dict = oracle_dict
        self.script = script_dict["script"]
        self.oracle = oracle_dict["oracle"]
        self.interval = interval
        self.end = end
        self.logger = getLogger()
        self.log_file = log_file
        self.timeout = oracle_dict["timeout"]
        self.test_path = Configuration.putConf['test_path']
        self.test_mode = Configuration.putConf['test_mode']
        self.timeout_flag = False
        if "check_for_absence" in oracle_dict:
            self.check_for_absence = oracle_dict["check_for_absence"]
        else:
            self.check_for_absence = False

    def timeout_callback(self):
        self.timeout_flag = True


    def run(self):
        if self.test_mode == "Default":
            if self.test_path != "":
                self.logger.info(f"cd {self.test_path}")
                os.chdir( self.test_path )
            console2save = self.directory + '/' + str( self.id ) + "_console.txt"
            log2save = self.directory + '/' + str( self.id ) + "_log.txt"
            cov2save = self.directory + '/' + str( self.id ) + "_cov"

            # command = self.script + " > " + console2save + " 2>&1 ; " + "lcov --directory /postgresql-11.2 --capture --output-file --rc lcov_branch_coverage=1  " + cov2save + " "
            command = self.script + " > " + console2save + " 2>&1 ; "
            self.start_log_record()
            self.logger.info("---------------------" + command)
            # print("!!!!!!!!!!!!",os.environ)
            path_map = os.environ
            path_map["PATH"] = path_map["PATH"] + ":/home/hadoop/hadoop-3.1.3-work/bin"
            gc.collect()
            res = subprocess.Popen( command, shell=True, env=path_map)
            # res = subprocess.run(command, shell=True)
            if self.timeout == "default":
                self.timeout = 0
            #time.sleep( self.timeout )
            self.timeout_flag = False
            my_timer = Timer( self.timeout, self.timeout_callback, [])
            my_timer.start()
            while True:
                time.sleep(0.1)
                if self.timeout_flag == True:
                    break
                elif res.poll() != None:
                    break
                else:
                    pass
            self.logger.info("script execution finished")
            self.event_listener.push_observer_event( self.id )

            time.sleep( self.interval )

            self.stop_log_record( log2save )

            with open( console2save, 'r' ) as fp:
                raw_result = fp.read()

            self.result = self.check_oracle( raw_result )
        else:
            return

    def run_offline(self):

        console2save = self.directory + '/' + str( self.id ) + "_console.txt"

        try:
            with open( console2save, 'r' ) as fp:
                raw_result = fp.read()
        except Exception as e:
            raise ValueError("Unable to open file: " + console2save)

        self.result = self.check_oracle( raw_result )

    def start_log_record(self):
        if self.log_file == "":
            return
        try:
            with open( self.log_file, 'r' ) as fp:
                fp.read()
                self.file_index = fp.tell()
                # print("------start", self.file_index)
        except:
            self.file_index = 0


    def stop_log_record(self, log2save):
        if self.log_file == "":
            return
        try:
            with open( self.log_file, 'r' ) as fp:
                fp.seek( self.file_index )
                # print("------stop", self.file_index)
                result = fp.read()
        except:
            result = ""
        with open( log2save, 'w' ) as fp:
            fp.write( result )

    def nginx_stop_log_record(self, log2save):
        if self.log_file == "":
            return
        with open( "/tmp/error.log", 'r' ) as fp:
            result = fp.read()
        with open( log2save, 'w' ) as fp:
            fp.write( result )

    def check_oracle(self, raw_result):
        if self.check_for_absence and self.oracle not in raw_result:
            return True
        elif self.check_for_absence == False and self.oracle in raw_result:
            return True
        else:
            return False

    def bind(self, listener):
        self.event_listener = listener

    def set_directory(self, directory):
        self.directory = directory
