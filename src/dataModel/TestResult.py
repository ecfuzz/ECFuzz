from dataModel.CounterWriteToFileInterface import CounterWriteToFileInterface


class TestResult(CounterWriteToFileInterface):
    """
    This is a data model for test result in configuration fuzzing.

    Attributes:
        status (int): test status of test result.
        description (str): a short view of test result.
        failed_tests_count (int): count for failed unit tests.
        unitTestcasePath (str):
        trimmedTestcasePath (str):
    """

    def __init__(self, status: int = 0, sysFailType: int = 0, description: str = 'not set') -> None:
        super().__init__()
        self.status = status
        self.sysFailType = sysFailType
        self.description = description
        self.failed_tests_count = 0
        self.unitTestcasePath = ''
        self.trimmedTestcasePath = ''

    def __str__(self) -> str:
        return "TestResult(status:{0}, failed_tests_count:{1}, sysFailType:{2}, description:{3:10})".format(
            self.status,
            self.failed_tests_count,
            self.sysFailType,
            self.description)
