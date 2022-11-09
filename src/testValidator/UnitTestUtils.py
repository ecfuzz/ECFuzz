import sys, re, os
from typing import Dict, Tuple

from dataModel.Testcase import Testcase
from utils.Configuration import Configuration
import xml.etree.ElementTree as ET

from utils.Logger import Logger, getLogger


class UnitTestUtils(object):
    def __init__(self) -> None:
        self.logger = getLogger()
        self.project = Configuration.fuzzerConf['project']
        self.default_conf = self.load_default_conf(Configuration.putConf['default_conf_path'])

    def inject_config(self, param_value_pairs: dict) -> None:
        for p, v in param_value_pairs.items():
            self.logger.info(f">>>>[UnitTestUtils] injecting {p} with value {v}")

        if self.project in ["zookeeper", "alluxio"]:
            for inject_path in Configuration.putConf['injecting_location']:
                self.logger.info(">>>>[UnitTestUtils] injecting into file: {}".format(inject_path))
                with open(inject_path, "w") as file:
                    for p, v in param_value_pairs.items():
                        file.write(f"{p}={v}" + "\n")
        elif self.project in ["hadoop-common", "hadoop-hdfs", "hbase"]:
            conf = ET.Element("configuration")
            for p, v in param_value_pairs.items():
                prop = ET.SubElement(conf, "property")
                name = ET.SubElement(prop, "name")
                value = ET.SubElement(prop, "value")
                name.text = p
                value.text = v
            for inject_path in Configuration.putConf['injecting_location']:
                self.logger.info(">>>>[UnitTestUtils] injecting into file: {}".format(inject_path))
                with open(inject_path, "wb") as file:
                    file.write(str.encode(
                        "<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n"))
                    file.write(ET.tostring(conf))
        else:
            sys.exit(">>>>[UnitTestUtils] value injection for {} is not supported yet".format(self.project))

    def clean_config(self) -> None:
        self.logger.info(">>>> cleaning injected configuration from file")
        if self.project in ["zookeeper", "alluxio"]:
            for inject_path in Configuration.putConf['injecting_location']:
                with open(inject_path, "w") as file:
                    file.write("\n")
        elif self.project in ["hadoop-common", "hadoop-hdfs", "hbase"]:
            conf = ET.Element("configuration")
            for inject_path in Configuration.putConf['injecting_location']:
                with open(inject_path, "wb") as file:
                    file.write(str.encode(
                        '<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n'))

                    file.write(ET.tostring(conf))
        else:
            sys.exit(">>>>[UnitTestUtils] value injection for {} is not supported yet".format(self.project))

    def strip_ansi(self, s):
        # return ansi_escape.sub('', s)
        return re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]').sub('', s)

    def parse_surefire(self, clsname, expected_methods) -> Tuple[Dict,Dict]:
        """method expected to show up in surefire"""
        expected_methods = set(expected_methods)
        times = {}
        errors = {}
        try:
            fpath = None
            for surefire_path in Configuration.putConf['surefire_location']:
                self.logger.info("surefire_path is : {}".format(surefire_path))
                xml_path = os.path.join(surefire_path, "TEST-{}.xml".format(clsname))
                if os.path.exists(xml_path):
                    self.logger.info(f">>>>[UnitTestUtils] surefire report path: {xml_path}")
                    fpath = open(xml_path)
            tree = ET.parse(fpath)
            root = tree.getroot()
            tsinfo = root.attrib
            self.logger.info(">>>>[UnitTestUtils] test class outcome: {}".format(tsinfo))
            for tc in tree.iter(tag="testcase"):
                self.logger.info(">>>>[UnitTestUtils] unit test outcome: {}".format(tc.attrib))
                tname = tc.attrib["name"]
                ttime = tc.attrib["time"]
                times[tname] = str(ttime)
                for error in tc.iter(tag="error"):
                    errors[tname] = self.strip_ansi(error.text)
                for failure in tc.iter(tag="failure"):
                    errors[tname] = self.strip_ansi(failure.text)

            # failed before executing test 1) test failed, but recorded as init method name
            # failed before executing test 2) test failed, but recorded as cls name
            # if there are more than one upexpected method recorded,
            # this way cannot match noshow tests with recorded failed methods
            unexpected = set(times.keys()) - expected_methods
            if len(unexpected) > 1:
                self.logger.info(">>>>[UnitTestUtils] [strange] there are more than one unexpected tests")
            expected_noshow = expected_methods - set(times.keys())
            for u in unexpected:
                for e in expected_noshow:
                    times[e] = times[u]
                    if u in errors:
                        errors[e] = errors[u]
            for u in unexpected:
                times.pop(u, None)
                errors.pop(u, None)

            # assertion
            if int(tsinfo["errors"]) + int(tsinfo["failures"]) != len(errors):
                self.logger.info(">>>>[UnitTestUtils] [strange] error count doesn't add up")
            if int(tsinfo["tests"]) != len(expected_methods):
                self.logger.info(">>>>[UnitTestUtils] [strange] # tests run doesn't add up")
            if set(times.keys()) != expected_methods:
                self.logger.info(">>>>[UnitTestUtils] [strange] tests run not the same as expected tests")
            fpath.close()
        except Exception as e:
            self.logger.info(">>>>[UnitTestUtils] failed to parse surefire file: {}".format(e))

        # pretty printing
        self.logger.info(">>>>[UnitTestUtils] result to be return:")
        for t, value in times.items():
            fulltname = f"{clsname}#{t}"
            if t in errors:
                self.logger.info(f"{fulltname} with running time {value} failed")
                self.logger.info(">>>>[UnitTestUtils] failed test output: {}".format(errors[t]))
            else:
                self.logger.info(f"{fulltname} with running time {times[t]} passed")
        return times, errors

    def load_default_conf(self, path: str) -> dict:
        """load default config, should be in /openctest/default_configs/"""
        with open(path) as fd:
            data = [x.strip("\n").split("\t") for x in fd]
            conf_map = {}
            for row in data:
                param, value = row[:2]
                conf_map[param] = value
        return conf_map

    def extract_conf_diff(self, testcase :Testcase) -> Dict[str, str]:
        """get the conf diff based on the default conf

        Args:
            testcase (TestCase): new testcase

        Returns:
            dict: different info of testcase
        """
        default_conf_map = self.default_conf
        new_conf_map = {}
        for confItem in testcase.confItemList:
            conf_name, conf_value = confItem.name, confItem.value
            new_conf_map[conf_name] = conf_value
        self.logger.info(">>>>[UnitTestUtils] default conf file: {}".format(Configuration.putConf['default_conf_path']))
        self.logger.info(">>>>[UnitTestUtils] new input conf file: {} (param, value) pairs".format(len(new_conf_map.keys())))
        conf_diff = {}
        for param, value in new_conf_map.items():
            if param not in default_conf_map:
                self.logger.info(">>>>[UnitTestUtils] parameter {} in input config file is not in default config file".format(param))
            if param not in default_conf_map or new_conf_map[param] != default_conf_map[param]:
                conf_diff[param] = value
        self.logger.info(">>>>[UnitTestUtils] config diff: {} (param, value) pairs".format(len(conf_diff)))
        return conf_diff

