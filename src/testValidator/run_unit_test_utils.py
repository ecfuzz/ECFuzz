import re
from typing import Set, List, Tuple

from utils.Logger import Logger, getLogger
from utils.Configuration import Configuration

class run_unit_test_utils(object):
    def __init__(self) -> None:
        self.logger = getLogger()
        # self.use_surefire = False
        # self.display_mode = False
        # self.cmd_timeout = None

    def maven_cmd(self, test: str, add_time=False) -> List[str]:
        # surefire:test reuses test build from last compilation
        # if you modified the test and want to rerun it, you must use `mvn test`
        mvn_cmd =[]
        test_mode = "surefire:test" if Configuration.fuzzerConf['use_surefire'] == 'True' else "test"
        maven_args = ["-DfailIfNoTests=false", "-Dcheckstyle.skip", "-Dlicense.skip", "-Dfindbugs.skip", "-Dmaven.javadoc.skip=true"] if Configuration.fuzzerConf['project'] == "alluxio" else []
        # cmd = ["mvn", test_mode, "-Dtest={}".format(test)]
        # cmd = "mvn {} -Dtest={}".format(test_mode, test)
        if Configuration.fuzzerConf['project'] == "alluxio":
            mvn_cmd = ["mvn", "license:format" ,test_mode, "-Dtest={}".format(test)] + maven_args
        else:
            mvn_cmd = ["mvn" ,test_mode, "-Dtest={}".format(test)] + maven_args
        # if add_time:
        #     cmd = ["time"] + cmd
        # self.logger.info(">>>>[run_unit_test_utils] command: " + " ".join(cmd))
        self.logger.info(f">>>>[run_unit_test_utils] command is : {mvn_cmd}")
        return mvn_cmd
    
    def split_tests_by_cls(self, associated_tests: Set[str]) -> List[str]:
        """
        split tests by it's class for later parse surefire reports
        """
        d1 = {}
        res = []
        for tests in associated_tests:
            classname, method = tests.split("#")
            if classname not in d1:
                d1[classname] = set()
            d1[classname].add(method)
        # construct str for mvn test
        for classname in d1:
            # init the str
            curStr = classname + "#"
            curStr += "+".join(list(d1[classname]))
            res.append(curStr)
        return res
    
    def cal_strs(self, tests: List[str]) -> str:
        res = ""
        for ts in tests:
            res = res + ts + ","
        return res[:-1]
    
    def is_failed(self, line: str) -> bool:
        if line.find("Tests run") != -1:
            fail = line.find("Failures:")
            error = line.find("Errors:")
            if fail == -1 or error == -1:
                return False
            falinum = line[fail+9: fail+11]
            errornum = line[error+9: error+11]
            if falinum != " 0" or errornum != " 0":
                return True
            return False
        else:
            return False
            
    def deal_line_info(self, line_info: str) -> Tuple[int, bool]:
        """deal with line info

        Args:
            self (_type_): _description_
            bool (_type_): _description_

        Returns:
            _type_: first: total_run tests
                    second: whether it needs to be killed by pre.failed or not (failed means True)
        """
        # return int: tests run count
        # return bool: failed or not (failed means True)
        res = re.search(r'Tests run:.*Failures:.*Errors:.*Skipped.*Time elapsed', line_info)
        if res:
            # means it has info we want (all needs to be cal)
            try:
                strs = res.group()
                failure = strs.find("Failures")
                errors = strs.find("Errors")
                skipped = strs.find("Skipped")
                total_run = int(strs[10: failure-2])
                fail_num = int(strs[failure + 9: errors-2])
                error_num = int(strs[errors + 7: skipped-2])
                flag = False
                if fail_num != 0 or error_num != 0:
                    flag = True
                self.logger.info(f"<<<<[unit utils] flag is : {flag}, total_run is : {total_run}, fail is : {fail_num}, error is : {error_num}")
                return total_run, flag 
            except Exception as e:
                self.logger.info(f"<<<<[unit utils] exception is : {e}")
                return 0, False
        else:
            return 0, False

    def strip_ansi(self, s: str) -> object:
        return re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]').sub('', s)

    def join_test_string(self, tests) -> str:
        test_by_cls = self.group_test_by_cls(tests)
        ret = ""
        for clsname, methods in test_by_cls.items():
            ret += clsname
            ret += "#"
            ret += "+".join(list(methods))
            ret += ","
        return ret

    def group_test_by_cls(self, tests) -> dict:
        d = {}
        for t in tests:
            clsname, method = t.split("#")
            if clsname not in d:
                d[clsname] = set()
            d[clsname].add(method)
        return d

    def reverse_map(self, map) -> dict:
        # test -> params
        r_map = {}
        for param in map.keys():
            for test in map[param]:
                if test not in r_map.keys():
                    r_map[test] = set()
                r_map[test].add(param)
        return r_map

    def encode_signature(self, params, tested_params) -> str:
        signature = ""
        for i in range(len(params)):
            param = params[i]
            signature = f"{signature}1" if param in tested_params else f"{signature}0"
        assert len(signature) == len(params)
        return signature

    def decode_signature(self, params, signature) -> str:
        assert len(signature) == len(params)
        return {params[i] for i in range(len(signature)) if signature[i] == "1"}

    def split_tests(self, associated_test_map) -> list:
        """split test to rule out value assumption interference"""
        reversed_map = self.reverse_map(associated_test_map)
        params = sorted(list(associated_test_map.keys()))
        group_map = {}
        for test in reversed_map.keys():
            signature = self.encode_signature(params, reversed_map[test])
            if signature not in group_map.keys():
                group_map[signature] = set()
            group_map[signature].add(test)

        for sig in group_map:
            tested_params = self.decode_signature(params, sig)
            group_map[sig] = (tested_params, group_map[sig])

        return list(group_map.values())
