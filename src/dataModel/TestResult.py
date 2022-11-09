from dataModel.CounterWriteToFileInterface import CounterWriteToFileInterface


class TestResult(CounterWriteToFileInterface):
    """
    This is a data model for test result in configuration fuzzing.
    """

    def __init__(self, status: int = 0, description: str = 'not set') -> None:
        super().__init__()
        self.status = status
        self.description = description
        self.failed_tests_count = 0
        self.unitTestcasePath = ''
        self.trimmedTestcasePath = ''

    def __str__(self) -> str:
        return "TestResult(status:{0}, failed_tests_count:{1}, description:{2:10})".format(
            self.status,
            self.failed_tests_count,
            self.description)
