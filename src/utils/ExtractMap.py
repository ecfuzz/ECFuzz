import json
from typing import Dict, List

from utils.UnitConstant import *
from utils.Logger import Logger, getLogger


class ExtractMap(object):
    """extract mapping of ctest

    Args:
        object (_type_): _description_
    """

    def __init__(self, project) -> None:
        self.logger = getLogger()
        self.project = project

    def loadMapping(self) -> dict:
        with open(MAPPING[self.project]) as map_file:
            res = json.load(map_file)
        return res

    def parseMap(self, confMap: dict) -> dict:
        """get the given conf's ctests

        Args:
            confMap (dict): key, value : confName, confValue

        Returns:
            dict: confName, relatedTests
        """
        mapping = self.loadMapping()
        return {conf: mapping[conf] for conf in confMap if conf in mapping}

    def extract_mapping(self, mapping: Dict, params: List):
        """get tests associated with a list of params from mapping"""
        data = {}
        selected_tests = []
        for p in params:
            if p in mapping:
                tests = mapping[p]
                self.logger.info(">>>>[ExtractMap] parameter {} has {} tests".format(p, len(tests)))
                data[p] = tests
                selected_tests = selected_tests + tests
            else:
                self.logger.info(">>>>[ExtractMap] parameter {} has 0 tests".format(p))
        return data, set(selected_tests)
