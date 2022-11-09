from typing import Dict

from dataModel.Testcase import Testcase
from abc import ABCMeta, abstractmethod

from testValidator.SystemTester import SystemTester
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration


class Trimmer(object, metaclass=ABCMeta):
    """
    Trimmer tries to make a testcase that can trigger a vulnerability to be as simple as possible.
    """

    def __init__(self, systemTester: SystemTester = None, defaultValueMap: Dict[str, str] = None):
        self.systemTester: SystemTester = systemTester
        if defaultValueMap is None:
            confItems = ConfAnalyzer.confItemsBasic + ConfAnalyzer.confItemsMutable
            confItemValueMap = ConfAnalyzer.confItemValueMap
            self.defaultValueMap = {name: confItemValueMap[name] for name in confItems}
        else:
            self.defaultValueMap = defaultValueMap

    @abstractmethod
    def trimTestcase(self, testcase: Testcase) -> Testcase:
        """
        Simplify a testcase to keep minimal but still capable to trigger a vulnerability.

        Args:
            testcase: original testcase

        Returns:
            trimmedTestcase (Testcase): a trimmed testcase
        """
        pass