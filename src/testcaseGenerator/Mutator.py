from abc import ABCMeta, abstractmethod
from dataModel.Seed import Seed
from dataModel.Testcase import Testcase

class Mutator(object, metaclass=ABCMeta):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def mutate(self, seed: Seed) -> Testcase:
        """
        Perform some mutation on the configuration items of a seed, so as to generate a testcase.

        Args:
            seed (Seed): a seed needed to be mutated.
            constraint (Constraint): a map that guides how to perform mutation.

        Returns:
            testcase (Testcase): a new testcase.
        """
        pass
