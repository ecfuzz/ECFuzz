
from abc import abstractmethod


class TrimCtestsInterface(object):
    """to trim tests for decrease the test time

    Args:
        object (_type_): _description_
    """
    def __init__(self) -> None:
        pass

    @abstractmethod
    def trimCtests(self, tests_map: dict) -> dict:
        """trim tests by different methods

        Args:
            tests_map (dict): original conf and it's tests.

        Returns:
            dict: new tests of original conf, it will decrease the ctests
        """
        pass