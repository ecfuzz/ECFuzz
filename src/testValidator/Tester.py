
from abc import ABCMeta, abstractmethod

from dataModel.TestResult import TestResult
from dataModel.Testcase import Testcase


class Tester(object, metaclass=ABCMeta):
    """
    A Tester is able to perform a testing based on a given testcase and some
    environment settings.
    """
    def __init__(self) -> None:
        pass

    @abstractmethod
    def runTest(self, testcase: Testcase) -> TestResult:
        """
        Perform a testing based on a given testcase.

        Args:
            testcase (Testcase): a Testcase.

        Returns: testResult (TestResult): a TestResult that contains information about the running status and results
        of this testing.
        """
        pass
