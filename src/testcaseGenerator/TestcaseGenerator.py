from dataModel.Seed import Seed
from dataModel.Testcase import Testcase
from testcaseGenerator.StackedMutator import Mutator
from utils.ShowStats import ShowStats


class TestcaseGenerator(object):
    """
    Testcase Generator is responsible for generating a testcase based on a given seed.
    A Testcase Generator may have different implements via different combination of mutators and constraintMaps.
    """

    def __init__(self, mutator: Mutator) -> None:
        self.mutator = mutator


    def mutate(self, seed: Seed) -> Testcase:
        """
        Perform some mutation on the configuration items of a seed, so as to generate a testcase.
        Based on the constraint map it contains.

        Args:
            seed (Seed): a seed needed to be mutated.

        Returns:
            testcase (Testcase): a new testcase.
        """
        ShowStats.currentJob = 'mutating'
        return self.mutator.mutate(seed)
