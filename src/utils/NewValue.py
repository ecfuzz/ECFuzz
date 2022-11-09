# some special param's value
FILEPATHS = ["/valid/file1", "/valid/file2"]
DIRPATHS = ["/valid/dir1", "/valid/dir2"]
USERS = ['xdsuper', 'samsuper']
GROUPS = ['xdgroup', 'samgroup']
PORTS = ["3000", "3001"]
NAMESERVICES = ["ns1", "ns2"]
INTERFACES = ["eth1", "eth2"]
IPS = ["127.0.0.1"]
PERMISSIONMASKS = ["007", "002"]
PERMISSIONCODES = ["rwx------", "rwxrwx---"]
timeunits = ["ms", "millisecond", "s", "sec", "second", "m", "min", "minute", "h", "hr", "hour", "d", "day"]
datasize = ["MB"]

import random,re,sys
from utils.IdentifyType import IdentifyType
from dataModel.ConfItem import ConfItem
from utils.ShowStats import ShowStats

class NewValue(object):
    """
    Constraint contains how to generate values for different types of configuration items.
    """
    def __init__(self) -> None:
        pass

    def constraint_method(self, constraint_type: str, confItemA: ConfItem, confItemB: ConfItem):
        if constraint_type == "Control Dependency":
            if confItemA.type == "BOOL":
                ShowStats.nowTestConfigurationName = confItemA.name
                ShowStats.nowMutationType = confItemA.type
                confItemA.value = self.genValue(confItemA.type, confItemA.value)
            else:
                if confItemB.type == "BOOL":
                    ShowStats.nowTestConfigurationName = confItemB.name + ","
                    ShowStats.nowMutationType = confItemB.type + ","
                    confItemB.value = "True"
                if ShowStats.nowTestConfigurationName.endswith(","):
                    ShowStats.nowTestConfigurationName = ShowStats.nowTestConfigurationName + confItemA.name
                    ShowStats.nowMutationType = ShowStats.nowMutationType + confItemA.type
                else:
                    ShowStats.nowTestConfigurationName = confItemA.name
                    ShowStats.nowMutationType = confItemA.type

                confItemA.value = self.genValue(confItemA.type, confItemA.value)

        elif constraint_type == "Value Relationship Dependency":
            ShowStats.nowTestConfigurationName = confItemA.name + "," + confItemB.name
            ShowStats.nowMutationType = confItemA.type + "," + confItemB.type
            confItemA.value = self.genValue(confItemA.type, confItemA.value)
            confItemB.value = self.genValue(confItemB.type, confItemB.value)

        elif constraint_type == "Overwrite":
            ShowStats.nowTestConfigurationName = confItemA.name
            ShowStats.nowMutationType = confItemA.type
            confItemA.value = self.genValue(confItemA.type, confItemA.value)

        elif constraint_type == "Default Value Dependency":
            ShowStats.nowTestConfigurationName = confItemA.name + "," + confItemB.name
            ShowStats.nowMutationType = confItemA.type + "," + confItemB.type
            confItemA.value = self.genValue(confItemA.type, confItemA.value)
            confItemB.value = confItemA.value

        elif constraint_type == "Behavior Dependency":
            ShowStats.nowTestConfigurationName = confItemA.name + "," + confItemB.name
            ShowStats.nowMutationType = confItemA.type + "," + confItemB.type
            confItemA.value = self.genValue(confItemA.type, confItemA.value)
            confItemB.value = self.genValue(confItemB.type, confItemB.value)

        else:
            raise Exception("unsupported dependencies")

    def genValue(self, confType: str, value: str) -> str:
        """
        To get a new value for the current type of configuration item.

        Args:
            confType (str): configuration item type

        Returns:
            value (str): a new value.
        """
        
        if(confType == "BOOL"):
            return self.genBool(value)
        if(confType == "PORT"):
            return self.genPort(value)
        if(confType == "PM"):
            return self.genPermissionMask(value)
        if(confType == "INT"):
            return str(self.genInt(value))
        if(confType == "FLOAT"):
            return str(self.genFloat(value))
        if(confType == "PC"):
            return self.genPermissionCode(value)
        if(confType == "INTLIST"):
            return str(self.genIntList(value))
        if(confType == "STRLIST"):
            return str(self.genStringList(value))
        if(confType == "IP"):
            return self.genIp(value)
        if(confType == "IPPORT"):
            return self.genIpPortAddr(value)
        if(confType == "CLASSNAME"):
            return self.genClassName(value)
        if(confType == "FILEPATH"):
            return self.genFilePath(value)
        if(confType == "TIME"):
            return self.genTime(value)
        if(confType == "DATA"):
            return self.genDataSize(value)
        if(confType == "DIRPATH"):
            return self.genDirPath(value)
        if(confType == "USER"):
            return self.genUser(value)
        if(confType == "GROUP"):
            return self.genGroup(value)
        if(confType == "NAMESERVICES"):
            return self.genNameservices(value)
        if(confType == "INTERFACE"):
            return self.genInterface(value)
        else:
            return ""

    # based old value to generate new value as a list
    def genBool(self, value: str) -> str:
        if value.lower() == "true":
            return "False"
        else:
            return "True"

    def genPort(self, value) -> str:
        return random.choice(PORTS)

    def genPermissionMask(self, value) -> str:
        return random.choice(PERMISSIONMASKS)

    def genInt(self, value) -> int:
        tmp = int(value)
        res = []
        res.append(tmp+1)
        res.append(tmp-1)
        res.append(tmp>>1)
        res.append(tmp<<1)
        res.append(0)
        res.append(-tmp)
        res.append(-1)
        res.append(sys.maxsize)
        res.append(-sys.maxsize-1)
        return random.choice(res)

    def genFloat(self, value) -> float:
        s = value
        tmp = re.match(r"^\d+\.\d+[fF]$", s)
        res =[]
        if tmp:
            s = s[:-1]
        val = float(s)
        res.append(val/2)
        res.append(val*2)
        res.append(-val)
        res.append(0.0)
        res.append(val+1)
        res.append(val-1)
        res.append(float(sys.maxsize))
        res.append(float(-sys.maxsize-1))
        return random.choice(res)

    def genPermissionCode(self, value) -> str:
        return random.choice(PERMISSIONCODES)

    def genIntList(self, value) -> list:
        # based on list to generate one list
        # same size compared to old list
        vals = value.split(",")
        res = []
        for val in vals:
            rand = random.random()
            if(rand < 0.1):
                res.append(int(val)<<1)
            elif(rand < 0.3):
                res.append(int(val)>>1)
            elif(rand < 0.5):
                res.append(0)
            elif(rand < 0.75):
                res.append(-int(val))
            elif(rand < 0.9):
                res.append(sys.maxsize)
            else:
                res.append(-sys.maxsize-1)
        return res

    def genStringList(self, value) -> list:
        vals = value.split(",")
        res = []
        for val in vals:
            if(len(val)>0):
                rand = random.random()
                length = len(val)//2
                if(rand < 0.1):
                    res.append("/"+val)
                elif(rand < 0.3):
                    res.append(val+"/")
                elif(rand < 0.5):
                    res.append("null")
                elif(rand < 0.75):
                    res.append(val[length:]+val[:length-1])
                elif(rand < 0.9):
                    res.append(val[:length])
                else:
                    res.append(val[length:])
            else:
                res.append(val)
        return res

    def genIp(slef, value) -> str:
        res = ["127.0.0.1","192.168.2.53"]
        return random.choice(res)

    def genIpPortAddr(self, value) -> str:
        s = value
        s = s[:s.find(":")]
        res =[]
        res.append(s+":"+str(PORTS[0]))
        res.append(s+":"+str(PORTS[1]))
        res.append(s+":"+"20000")
        res.append(s+":"+"22")
        res.append(s+":"+"65599")
        return random.choice(res)
        
    def genClassName(self, value) -> str:
        return value

    def genFilePath(self, value) -> str:
        return random.choice(FILEPATHS)

    def genTime(self, value) -> str:
        res = []
        s = value
        for unit in timeunits:
            if s.endswith(unit):
                t = s[:s.find(unit)]
                identifyType = IdentifyType()
                if identifyType.isInt(t):
                    t = int(t)
                    res.append("1"+unit)
                    res.append(str(2*t)+unit)
                    res.append(str(10*t)+unit)
                    res.append("0"+unit)
                    res.append("-"+str(t)+unit)
        return random.choice(res)

    def genDataSize(self, value) -> str:
        res = []
        s = value
        for unit in datasize:
            if(s.endswith(unit)):
                t = s[:s.find(unit)]
                identifyType = IdentifyType()
                if identifyType.isInt(t):
                    t = int(t)
                    res.append("1"+unit)
                    res.append(str(2*t)+unit)
                    res.append(str(10*t)+unit)
                    res.append("0"+unit)
                    res.append("-"+str(t)+unit)
        return random.choice(res)

    def genDirPath(self, value) -> str:
        return random.choice(DIRPATHS)

    def genUser(self, value) -> str:
        return random.choice(USERS)

    def genGroup(self, value) -> str:
        return random.choice(GROUPS)

    def genNameservices(self, value) -> str:
        return random.choice(NAMESERVICES)

    def genInterface(self, value) -> str:
        return random.choice(INTERFACES)