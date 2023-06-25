import os
from logging import raiseExceptions
from dataModel.Seed import Seed
from dataModel.Testcase import Testcase
from dataModel.ConfItem import ConfItem
from utils.ceit.OptionsForCEIT import OptionsForCEIT
from utils.ceit.misconf import MisconfEngine
from utils.Configuration import Configuration
from testcaseGenerator.Mutator import Mutator

import random, logging
from utils.UnitConstant import DATA_DIR
from utils.ShowStats import ShowStats
from utils.Logger import getLogger

class CeitMutator(Mutator):
    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger()
        self.optionsForCeit = OptionsForCEIT()
        self.options = self.optionsForCeit.run()
        self.misconf_engine = MisconfEngine()

    def mutate(self, seed: Seed) -> Testcase:
        testcase = Testcase()
        choose_conf_index = random.randint(0, len(seed.confItemList) - 1)
        
        for index in range(0, len(seed.confItemList)):
            item = ConfItem()
            conf = seed.confItemList[index]
            item.name = conf.name
            item.type = conf.type
            if index == choose_conf_index:
                option = None
                self.logger.info(f"<<<<[CEITMutator] for item conf name is : {conf.name}; conf value is : {conf.value}; conf type is : {conf.type}")

                for confInfo in self.options.values():
                    if confInfo["key"] == conf.name:
                        option = confInfo
                
                ShowStats.nowTestConfigurationName = conf.name
                ShowStats.nowMutationType = Configuration.fuzzerConf['misconf_mode'] + ":" + option["constraint"]
                
                mutants = self.misconf_engine.mutate( option )
                misconfIndex = random.randint(0, len(mutants) - 1) 
                misconf = mutants[misconfIndex] 
                if "value" in misconf:
                    err = misconf["value"]
                    self.logger.info("<<<<[CEITMutator] for option name is : {}; before_value is : {}; after_value is : {}; option constraint is : {}".format(option["key"], option["value"], err, option["constraint"])) 
                    item.value = err
                else:
                    self.logger.info("<<<<[CEITMutator] for option name is : {} generates 0 misconf.".format(option["key"])) 
                    item.value = "CeitMutator"
            else:
                item.value = conf.value
            testcase.confItemList.append(item)
        
        return testcase