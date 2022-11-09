import unittest
import sys

from dataModel.Seed import Seed
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration

sys.path.append("../../src")

from seedGenerator.SeedGenerator import SeedGenerator


class testSeedGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def testGenerateSeed(self):
        sg = SeedGenerator()

        seed = sg.generateSeed()
        print(seed)
        for confItem in sg.confItemsBasic:
            assert confItem not in seed.confItemList

        for _ in range(10):
            sg.generateSeed()

        sg.addSeedToPool(seed)

        for _ in range(10):
            sg.generateSeed()

    def testAddSeedToPool(self):
        sg = SeedGenerator()

        assert sg.seedPool.__len__() == 0

        sg.addSeedToPool(Seed())

        assert sg.seedPool.__len__() == 1


if __name__ == '__main__':
    unittest.main()
