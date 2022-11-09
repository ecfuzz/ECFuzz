import os.path , logging
import random

from dataModel.ConfItem import ConfItem
from dataModel.Seed import Seed
from dataModel.Testcase import Testcase
from testcaseGenerator.Mutator import Mutator
from utils.NewValue import NewValue
from utils.ConfAnalyzer import ConfAnalyzer
from utils.UnitConstant import DATA_DIR
from utils.ShowStats import ShowStats
from utils.Logger import Logger

class SingleMutator(Mutator):
    def __init__(self) -> None:
        super().__init__()
        self.logger: logging.Logger = Logger.get_logger()

    def findConfItem(self, seed: Seed, confName: str):
        """
        The findConfItem function takes in a seed and a confName.
        It then searches through the list of confItems for that seed to find the one with the name specified by confName.
        If it finds it, it returns its index and a ConfItem object containing its information (name, type, value).
        If not found, returns - 1 for index and None for ConfItem.

        Args:
            self: Reference the object of the class
            seed:Seed: Store the configuration items of the seed
            confName:str: Specify the name of a configuration item

        Returns:
            A tuple with the index of the configuration item and its value
        """
        confItemIndex = -1
        res = ConfItem()
        for index in range(0, len(seed.confItemList)):
            conf = seed.confItemList[index]
            if confName == conf.name:
                res.name = conf.name
                res.type = conf.type
                res.value = conf.value
                confItemIndex = index
                break
        if confItemIndex == -1:
            return confItemIndex, None
        else:
            return confItemIndex, res

    def mutate(self, seed: Seed) -> Testcase:
        """
       

        Args:
            seed:

        Returns:
            Testcase:

        """
        testcase = Testcase()
        choose_conf_index = random.randint(0, len(seed.confItemList) - 1)
        itemB_dict = {}
        
        dependency = ConfAnalyzer.confItemRelations
        newValue = NewValue()
        for index in range(0, len(seed.confItemList)):
            conf = seed.confItemList[index]
            itemA = ConfItem()
            itemA.name = conf.name
            itemA.type = conf.type
            itemA.value = conf.value
            self.logger.info(f"<<<<[SingleMutator] for itemA conf name is : {itemA.name}; conf value is : {itemA.value}; conf type is : {itemA.type}")
            
            if index == choose_conf_index:
                
                if conf.name in dependency.keys():
                    
                    for one in dependency[conf.name]:
                        
                        confItemIndex, itemB = self.findConfItem(seed, one[0])
                        
                        if confItemIndex == -1:
                            ShowStats.nowTestConfigurationName = conf.name
                            ShowStats.nowMutationType = conf.type
                            itemA.value = newValue.genValue(conf.type, conf.value)
                        
                        else:
                            self.logger.info(f"<<<<[SingleMutator] for itemB conf name is : {itemB.name}; conf value is : {itemB.value}; conf type is : {itemB.type}")
                            newValue.constraint_method(one[1], itemA, itemB)
                            self.logger.info(f"<<<<[SingleMutator] for new itemB conf name is : {itemB.name}; conf value is : {itemB.value}; conf type is : {itemB.type}")
                            itemB_dict[confItemIndex] = itemB 
                else:
                    ShowStats.nowTestConfigurationName = conf.name
                    ShowStats.nowMutationType = conf.type
                    itemA.value = newValue.genValue(conf.type, conf.value)
                # if (len(mutated_value_list)):
                #     new_value = mutated_value_list[random.randint(0, len(mutated_value_list) - 1)]
                #     co.value = str(new_value)
            else:
                itemA.value = conf.value
            testcase.confItemList.append(itemA)

        
        for index in itemB_dict:
            testcase.confItemList[index] = itemB_dict[index]
        return testcase
