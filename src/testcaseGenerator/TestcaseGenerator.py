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
        # self.seed_all = Seed()

    # def selfComplete(self, testcase: Testcase, project: str, conf_path: str) -> Testcase:
    #     
    #     newTestcase = Testcase()
    #     confParser = ConfParser(project)
    #     conItems = confParser.parse_conf_file(conf_path)

    #     testcase_name_list = []
    #     for one in testcase.confItemList:
    #         testcase_name_list.append(one.name) 
    #     
    #     for conf_name in conItems:
    #         conf_value = conItems[conf_name]
    #         identifyType = IdentifyType()
    #         conf_type = identifyType.run(conf_name, conf_value)
    #         confItem = ConfItem(conf_name, conf_type, conf_value)
    #         self.seed_all.confItemList.append(confItem)

    #     
    #     for seeditem in self.seed_all.confItemList:
    #         if seeditem.name in testcase_name_list:
    #             index = testcase_name_list.index(seeditem.name)
    #             newTestcase.confItemList.append(testcase.confItemList[index])
    #         else:
    #             newTestcase.confItemList.append(seeditem)
    #     return newTestcase

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
