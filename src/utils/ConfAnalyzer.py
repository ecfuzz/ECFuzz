from typing import Dict, List
from utils.ClassifyConfItems import ClassifyConfItems
from utils.Constraint import Constraint
from utils.ConfParser import ConfParser
from utils.Configuration import Configuration
from utils.Logger import getLogger
import json

class ConfAnalyzer(object):
    # input: project: str, conf_path: str, ctest_map_path:str
    # output:
    #{name:value}
    confItemValueMap : Dict[str, str] = {}
    #{name:type}
    confItemTypeMap : Dict[str, str] = {}
    confItemsBasic :List[str] = [] 
    confItemsMutable :List[str] = []

    #{confa:[[confb,contorl],[confc, dependency]],confa:[[confb,contorl],[confc, dependency]]}
    confItemRelations: Dict[str, List[List[str]]] = {}
    confUnitMap: Dict[str, List[str]] = {}
    
    excludeConf:List[str] = [] # the exclude conf
    confMutationInfo:Dict[str, List[int]] = {} # list[int](mutationNumber, firstBugNumber) 

    @staticmethod
    def analyzeConfItems() -> None:
        with open(Configuration.putConf['unit_test_mapping_path']) as map_file:
            ConfAnalyzer.confUnitMap = json.load(map_file)
        ConfAnalyzer.confItemValueMap, ConfAnalyzer.confItemTypeMap= ConfParser().parse_conf_file()
        # if (len(ConfAnalyzer.confItemValueMap) < 50):
        #     ConfAnalyzer.confItemsBasic = [] 
        #     for confName in ConfAnalyzer.confItemValueMap:
        #         ConfAnalyzer.confItemsMutable.append(confName)
        # else:
        #     ConfAnalyzer.confItemsBasic, ConfAnalyzer.confItemsMutable = ClassifyConfItems().run(ConfAnalyzer.confItemValueMap, ConfAnalyzer.confUnitMap)
        for confName in ConfAnalyzer.confItemValueMap:
            ConfAnalyzer.confItemsMutable.append(confName)
        # relations contains all configuration params
        ConfAnalyzer.confItemRelations = Constraint().getConstraintMap()
        # init the confMutationInfo
        for confName in ConfAnalyzer.confItemValueMap:
            if confName not in ConfAnalyzer.confMutationInfo:
                ConfAnalyzer.confMutationInfo[confName] = [0, 0]


