import copy
import csv
import random
from typing import List, Tuple, Dict

from dataModel.ConfItem import ConfItem
from dataModel.Seed import Seed
from utils.ConfAnalyzer import ConfAnalyzer
from utils.Configuration import Configuration
from utils.Logger import getLogger
from utils.ShowStats import ShowStats


class SeedGenerator(object):
    """
    Seed Generator is responsible for generating high quality seeds according to the information
    offered by `ConfAnalyzer`.
    """

    def __init__(self) -> None:
        self.logger = getLogger()
        self.seedPool: List[Seed] = []
        fuzzerConf = Configuration.fuzzerConf

        self.seedPoolSelectionRatio = float(fuzzerConf['seed_pool_selection_ratio'])

        # 加载配置项信息（运行成功的前提是ConfAnalyzer已经完成了分析）
        self.confItemsBasic: List[str] = ConfAnalyzer.confItemsBasic
        self.confItemMutable: List[str] = ConfAnalyzer.confItemsMutable
        self.confItems: List[str] = self.confItemsBasic + self.confItemMutable
        self.confItemRelations: Dict[str, List[List[str, str]]] = ConfAnalyzer.confItemRelations
        self.confItemTypeMap: Dict[str, str] = ConfAnalyzer.confItemTypeMap
        self.confItemValueMap: Dict[str, str] = ConfAnalyzer.confItemValueMap
        self.lastGeneratedSeed = None

        self.logger.info("SeedGenerator initialized.")

    def generateSeed(self) -> Seed:
        """
        The generateSeed function generates a new seed.

        If the seed pool is not empty, there is a 50% chance that the last generated seed will be used as the new one.
        Otherwise, k random configuration items are selected from all possible configuration items and related ones
        (i.e., those with an edge in the dependency graph) to form a new Seed object. The value of k is determined by
        randomly choosing an integer between 1 and n where n denotes all possible configuration items in total.

        Args:
            self: Access the attributes and methods of the class in python

        Returns:
            Seed:
        """
        ShowStats.currentJob = 'generating seed'
        fromPool = self.seedPool.__len__() > 0 and random.random() > self.seedPoolSelectionRatio
        if fromPool:
            self.logger.info("Random Choose a Seed from pool.")
            self.lastGeneratedSeed = random.choice(self.seedPool)
        else:  
            self.logger.info("Try creating a Seed...")
            confItemList = copy.deepcopy(self.confItemMutable)
            if Configuration.fuzzerConf['mutator'].split(".")[-1] == "SingleMutator":
                k = 1
            else:
                k = random.randint(3, 6)
            random.shuffle(confItemList)
            confItemList = confItemList[:k]
            relatedConfItems = []
            for confItemName in confItemList:
                if self.confItemRelations.__contains__(confItemName):
                    relatedConfItems.extend(relation[0] for relation in self.confItemRelations[confItemName] if relation[0] in self.confItems)

            confItemList += relatedConfItems

            confItemList = [ConfItem(name, self.confItemTypeMap[name], self.confItemValueMap[name])
                            for name in confItemList]

            self.lastGeneratedSeed = Seed(confItemList)
            self.addSeedToPool(self.lastGeneratedSeed)

        return self.lastGeneratedSeed

    def addSeedToPool(self, seed: Seed) -> None:
        """
        Add a seed that may be interesting to the seed pool.

        Args:
            seed: a possibly interesting seed.

        Returns:
            None
        """
        self.seedPool.append(seed)
        ShowStats.queueLength += 1
