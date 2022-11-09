import os
from logging import raiseExceptions
from dataModel.Seed import Seed
from dataModel.Testcase import Testcase
from dataModel.ConfItem import ConfItem
from testcaseGenerator.Mutator import Mutator
import random, logging
from utils.NewValue import NewValue
from utils.ConfAnalyzer import ConfAnalyzer
from utils.UnitConstant import DATA_DIR
from utils.ShowStats import ShowStats
from utils.Logger import Logger

class SmartMutator(Mutator):
    def __init__(self) -> None:
        super().__init__()
        self.logger: logging.Logger = Logger.get_logger()

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
        """
       

        Args:
            seed:
            constraint:

        Returns:
            Testcase:

        """
        testcase = Testcase()
        # number = [i for i in range(3, 6)]
        # mutate_num = number[random.randint(0, len(number) - 1)]
        mutate_num = 0
        if ShowStats.stackMutationFlag == 1:
            mutate_num = seed.confItemList.__len__()
        elif ShowStats.stackMutationFlag == 0:
            mutate_num = 1
        else:
            pass
        item_dict = {}
        
        dependency = ConfAnalyzer.confItemRelations
        newValue = NewValue()
        # index_list = random.sample(range(0, len(seed.confItemList)), mutate_num)

        for times in range(0, mutate_num):
            choose_conf_index = random.randint(0, len(seed.confItemList) - 1)
            conf = seed.confItemList[choose_conf_index]
            itemA = ConfItem()
            itemA.name = conf.name
            itemA.type = conf.type
            itemA.value = conf.value
            self.logger.info(f"<<<<[StackedMutator] for itemA conf name is : {itemA.name}; conf value is : {itemA.value}; conf type is : {itemA.type}")
            
            if conf.name in dependency.keys():
                
                for one in dependency[conf.name]:
                    
                    confItemIndex, itemB = self.findConfItem(seed, one[0])
                    
                    if confItemIndex == -1:
                        ShowStats.nowTestConfigurationName = conf.name
                        ShowStats.nowMutationType = conf.type
                        itemA.value = newValue.genValue(conf.type, conf.value)
                    
                    else:
                        self.logger.info(f"<<<<[StackedMutator] for itemB conf name is : {itemB.name}; conf value is : {itemB.value}; conf type is : {itemB.type}")
                        newValue.constraint_method(one[1], itemA, itemB)
                        self.logger.info(f"<<<<[StackedMutator] for new itemB conf name is : {itemB.name}; conf value is : {itemB.value}; conf type is : {itemB.type}")
                        item_dict[confItemIndex] = itemB
            else:
                ShowStats.nowTestConfigurationName = conf.name
                ShowStats.nowMutationType = conf.type
                itemA.value = newValue.genValue(conf.type, conf.value)
                # if (len(mutated_value_list)):
                #     new_value = mutated_value_list[random.randint(0, len(mutated_value_list) - 1)]
                #     co.value = str(new_value)
            item_dict[choose_conf_index] = itemA
            self.logger.info(f"<<<<[StackedMutator] for new itemA conf name is : {itemA.name}; conf value is : {itemA.value}; conf type is : {itemA.type}")
        
        for index in range(0, len(seed.confItemList)):
            if index in item_dict.keys():
                testcase.confItemList.append(item_dict[index])
            else:
                testcase.confItemList.append(seed.confItemList[index])
        return testcase


    # def mutate(self, seed: Seed, constraint: Constraint, method: int) -> Testcase:
    #     """
    #    

    #     Args:
    #         seed:
    #         constraint:

    #     Returns:
    #         Testcase:

    #     """
    #     testcase = Testcase()
    #     number = [i for i in range(3, 6)]
    #     mutate_num = number[random.randint(0, len(number) - 1)]
    #     itemB_dict = {}
    #     
    #     dependency = constraint.getConstraintMap(os.path.join(DATA_DIR, "cDep_result/intra.csv"))
    #     if method == 1:
    #         
    #         index_list = random.sample(range(0, len(seed.confItemList)), mutate_num)

    #         for index in range(0, len(seed.confItemList)):
    #             conf = seed.confItemList[index]
    #             itemA = ConfItem()
    #             itemA.name = conf.name
    #             itemA.type = conf.type
    #             itemA.value = conf.value
    #             if index in index_list:
    #                 
    #                 if conf.name in dependency.keys():
    #                     
    #                     for one in dependency[conf.name]:
    #                         
    #                         confItemIndex, itemB = self.findConfItem(seed, one[0])
    #                         
    #                         if confItemIndex == -1:
    #                             itemA.value = constraint.genValue(conf.type, conf.value)
    #                         
    #                         else:
    #                             constraint.constraint_method(one[1], itemA, itemB)
    #                             itemB_dict[confItemIndex] = itemB
    #                 else:
    #                     itemA.value  = constraint.genValue(conf.type, conf.value)
    #                 # if (len(mutated_value_list)):
    #                 #     new_value = mutated_value_list[random.randint(0, len(mutated_value_list) - 1)]
    #                 #     co.value = str(new_value)
    #             else:
    #                 itemA.value = conf.value
    #             testcase.confItemList.append(itemA)

    #     elif method == 2:
    #         
    #         cnt = 0
    #         start = 0
    #         if len(seed.confItemList) < mutate_num:
    #             mutate_num = len(seed.confItemList)
    #         else:
    #             start = random.randint(0, len(seed.confItemList) - mutate_num - 1)
    #         for index in range(start, len(seed.confItemList)):
    #             conf = seed.confItemList[index]
    #             itemA = ConfItem()
    #             itemA.name = conf.name
    #             itemA.type = conf.type
    #             itemA.value = conf.value
    #             
    #             if conf.name in dependency.keys():
    #                 
    #                 for one in dependency[conf.name]:
    #                     
    #                     confItemIndex, itemB = self.findConfItem(seed, one[0])
    #                     
    #                     if confItemIndex == -1:
    #                         itemA.value = constraint.genValue(conf.type, conf.value)
    #                     
    #                     else:
    #                         constraint.constraint_method(one[1], itemA, itemB)
    #                         itemB_dict[confItemIndex] = itemB
    #             else:
    #                 itemA.value  = constraint.genValue(conf.type, conf.value)
    #             cnt += 1
    #             testcase.confItemList.append(itemA)
    #             if(cnt == mutate_num):
    #                 break
    #     else:
    #         raiseExceptions("now only support two methods")

    #     
    #     for index in itemB_dict:
    #         testcase.confItemList[index] = itemB_dict[index]

    #     return testcase