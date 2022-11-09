import re
from typing import Set, List

from utils.Logger import Logger, getLogger


class run_unit_test_utils(object):
    def __init__(self) -> None:
        self.logger = getLogger()
        self.use_surefire = False
        self.display_mode = False
        self.cmd_timeout = None

    def maven_cmd(self, test: str, add_time=False) -> str:
        # surefire:test reuses test build from last compilation
        # if you modified the test and want to rerun it, you must use `mvn test`
        test_mode = "surefire:test" if self.use_surefire else "test"
        cmd = ["mvn", test_mode, "-Dtest={}".format(test)]
        if add_time:
            cmd = ["time"] + cmd
        self.logger.info(">>>>[run_unit_test_utils] command: " + " ".join(cmd))
        return cmd
    
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
