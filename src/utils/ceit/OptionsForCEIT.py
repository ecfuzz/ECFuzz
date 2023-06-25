from typing import Dict
from utils.ConfAnalyzer import ConfAnalyzer

class OptionsForCEIT(object):
    def __init__(self) -> None:
        self.confItemTypeMap: Dict[str, str] = ConfAnalyzer.confItemTypeMap
        self.confItemValueMap: Dict[str, str] = ConfAnalyzer.confItemValueMap
        self.confItemCtMap = {}
        self.confOptions = {}
    
    def typeTransformHelper(self, confType: str) -> str:
        constraint = "SPECSTR" 
        if confType == "NOTYPE":
            constraint = "SPECSTR"
        if confType == "INT":
            constraint = "NUM[INT,,,]"
        if confType == "FLOAT": 
            constraint = "NUM[FLOAT,0,,]"
        if confType == "BOOL": 
            constraint = "BOOL"
        if confType == "DIRPATH": 
            constraint = "PATH[,N,D]"
        if confType == "FILEPATH": 
            constraint = "PATH[,N,F]"
        if confType == "IP": 
            constraint = "IP"
        if confType == "PORT": 
            constraint = "PORT"
        if confType == "IPPORT": 
            constraint = "SPECSTR"
        if confType == "CLASSNAME": 
            constraint = "SPECSTR"
        if confType == "INTLIST": 
            constraint = "SPECSTR"
        if confType == "STRLIST": 
            constraint = "SPECSTR"
        if confType == "TIME": 
            constraint = "SPECSTR"
        if confType == "DATA": 
            constraint = "ENUM"
        if confType == "PC": 
            constraint = "SPECSTR"
        if confType == "PM": 
            constraint = "PERMISSION"
        if confType == "ZKDIR": 
            constraint = "SPECSTR"
        if confType == "ZKPORT": 
            constraint = "SPECSTR"
        if confType == "ZKPORTADDRESS": 
            constraint = "SPECSTR"
        if confType == "ZKLIMIT": 
            constraint = "SPECSTR"
        if confType == "ZKSIZE": 
            constraint = "SPECSTR"
        if confType == "ALGORITHM": 
            constraint = "SPECSTR"
        if confType == "USER": 
            constraint = "SPECSTR"
        if confType == "GROUP": 
            constraint = "SPECSTR"
        if confType == "NAMESERVICES": 
            constraint = "SPECSTR"
        if confType == "INTERFACE": 
            constraint = "SPECSTR"
        if confType == "POTENTIALFLOAT": 
            constraint = "SPECSTR"
        if confType == "UNKNOWN": 
            constraint = "SPECSTR"
        return constraint 
        
    def typeTransform(self): 
        for confName, confType in self.confItemTypeMap.items():
            constraint = self.typeTransformHelper(confType)
            self.confItemCtMap[confName] = constraint
             
    def createOptions(self):
        i = 0
        
        for confName, confValue in self.confItemValueMap.items(): 
            i = i + 1
            temp = {}
            temp["key"] = confName
            temp["value"] = confValue
            temp["constraint"] = self.confItemCtMap[confName]
            self.confOptions[str( i )] = temp
    
    def run(self) -> dict:
        self.typeTransform()
        self.createOptions()
        return self.confOptions