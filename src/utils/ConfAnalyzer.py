from typing import Dict, List
from utils.ClassifyConfItems import ClassifyConfItems
from utils.Constraint import Constraint
from utils.ConfParser import ConfParser
from utils.Configuration import Configuration
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

    @staticmethod
    def analyzeConfItems() -> None:
        with open(Configuration.putConf['unit_test_mapping_path']) as map_file:
            ConfAnalyzer.confUnitMap = json.load(map_file)
        ConfAnalyzer.confItemValueMap, ConfAnalyzer.confItemTypeMap= ConfParser().parse_conf_file()
        ConfAnalyzer.confItemsBasic, ConfAnalyzer.confItemsMutable = ClassifyConfItems().run(ConfAnalyzer.confItemValueMap, ConfAnalyzer.confUnitMap)
        ConfAnalyzer.confItemRelations = Constraint().getConstraintMap(ConfAnalyzer.confItemsBasic)


