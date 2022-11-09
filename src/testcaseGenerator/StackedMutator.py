import os
from logging import raiseExceptions
from dataModel.Seed import Seed
from dataModel.Testcase import Testcase
from dataModel.ConfItem import ConfItem
from testcaseGenerator.Mutator import Mutator
import random
from utils.NewValue import NewValue
from utils.ConfAnalyzer import ConfAnalyzer
from utils.UnitConstant import DATA_DIR
from utils.ShowStats import ShowStats

class StackedMutator(Mutator):
    def __init__(self) -> None:
        super().__init__()

    def findConfItem(self, seed: Seed, confName: str):
        confItemIndex = -1
        res = ConfItem()
        for index in range(0, len(seed.confItemList)):
            conf = seed.confItemList[index]
            if confName == conf.name:
                res.name = conf.name
                res.value = conf.value
                res.type = conf.type
                confItemIndex = index
                break
        if confItemIndex == -1:
            return confItemIndex, None
        else:
            return confItemIndex, res

    def mutate(self, seed: Seed) -> Testcase:
        testcase = Testcase()
        mutate_num = seed.confItemList.__len__()
        item_dict = {}
        dependency = ConfAnalyzer.confItemRelations
        newValue = NewValue()
        
        for times in range(0, mutate_num):
            choose_conf_index = random.randint(0, len(seed.confItemList) - 1)
            conf = seed.confItemList[choose_conf_index]
            itemA = ConfItem()
            itemA.name = conf.name
            itemA.type = conf.type
            itemA.value = conf.value
            if conf.name in dependency.keys():
                for one in dependency[conf.name]:
                    confItemIndex, itemB = self.findConfItem(seed, one[0])
                    if confItemIndex == -1:
                        ShowStats.nowTestConfigurationName = conf.name
                        ShowStats.nowMutationType = conf.type
                        itemA.value = newValue.genValue(conf.type, conf.value)
                    else:
                        newValue.constraint_method(one[1], itemA, itemB)
                        item_dict[confItemIndex] = itemB
            else:
                ShowStats.nowTestConfigurationName = conf.name
                ShowStats.nowMutationType = conf.type
                itemA.value = newValue.genValue(conf.type, conf.value)
            item_dict[choose_conf_index] = itemA

        for index in range(0, len(seed.confItemList)):
            if index in item_dict.keys():
                testcase.confItemList.append(item_dict[index])
            else:
                testcase.confItemList.append(seed.confItemList[index])
        return testcase