# some special param's value
FILEPATHS = ["/valid/file1", "/valid/file2", "/dev/shm", "@name@", "///file"]
DIRPATHS = ["/valid/dir1", "/valid/dir2", "/dev/shm", "valid/dir", "@name@", "file:///root/hdfs"]
USERS = ['xdsuper', 'samsuper', "hadoop", "+-#$", "12", "root"]
GROUPS = ['xdgroup', 'samgroup', "hadoop", "+-#$", "12", "root"]
PORTS = ["3000", "3001", "80", "0", "-1", "65599", "@@", "[names]"]
NAMESERVICES = ["ns1", "ns2", "@root", "11"]
INTERFACES = ["eth1", "eth2", "0", "@[+]@"]
IPS = ["127.0.0.1"]
PERMISSIONMASKS = ["007", "002", "999", "rwx", "4444", "777", "755"]
PERMISSIONCODES = ["rwx------", "rwxrwx---", "rwx++++++" ,"oxw---ikd", "111", "#&^%Zio"]
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


    def genStr(self, max_length: int, char_start: int = 32, char_range: int = 90) -> str:
        string_length = random.randrange(0, max_length + 1)
        out = ""
        for i in range(0, string_length):
                out += chr(random.randrange(char_start, char_start + char_range))
        return out

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
            return value

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
        res = [tmp + 1, tmp - 1, tmp >> 1, tmp << 1, 0, -tmp, -1, 99999999, -99999999, 2**32 - 1, -2**32]

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
        res.append(-1.0)
        res.append(float(2**32-1))
        res.append(float(-2**32))
        res.append(99999999.8)
        res.append(-99999999.8)
        return random.choice(res)

    def genPermissionCode(self, value) -> str:
        return random.choice(PERMISSIONCODES)

    def genIntList(self, value) -> str:
        # based on list to generate one list
        # same size compared to old list
        vals = value.split(",")
        res = []
        for val in vals:
            rand = random.random()
            try:
                if(rand < 0.1):
                    res.append(int(val)<<1)
                elif(rand < 0.2):
                    res.append(-1)
                elif(rand < 0.3):
                    res.append(int(val)>>1)
                elif(rand < 0.4):
                    res.append(1)
                elif(rand < 0.5):
                    res.append(0)
                elif(rand < 0.6):
                    res.append(0.0)
                elif(rand < 0.75):
                    res.append(-int(val))
                elif(rand < 0.9):
                    res.append(sys.maxsize)
                else:
                    res.append(-sys.maxsize-1)
            except Exception as e:
                res.append(val)
        return str(res)[1:-1]

    def genStringList(self, value) -> list:
        vals = value.split(",")
        res = []
        for val in vals:
            if (len(val)>0):
                rand = random.random()
                length = len(val)//2
                if (rand < 0.1):
                    res.append(f"/{val}")
                elif (rand < 0.2):
                    res.append(f"@/+{val}")
                elif (rand < 0.3):
                    res.append(f"{val}/")
                elif (rand < 0.4):
                    res.append(f"{val}@/-")
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
        return str(res)[1:-2]

    def genIp(self, value) -> str:
        res = ["127.0.0.1","192.168.2.53","0.0.0.0","728.59.66.723","255.255.255.255","isip@"]
        return random.choice(res)

    def genIpPortAddr(self, value) -> str:
        s = value
        s = s[:s.find(":")]
        res = [f"{s}:{str(PORTS[0])}", f"{s}:{str(PORTS[1])}", f"{s}:20000", f"{s}:22", f"{s}:65599", f"745.657.25.3:{str(PORTS[3])}",f"{s}:{str(PORTS[4])}"]

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
                    res.append("-100"+unit)
                    res.append("00x")
                    res.append("999999"+unit)
                    res.append("00s")
        if len(res) == 0:
            p = random.random()
            if p > 0.5:
                res.append("10"+ timeunits[0])
            else:
                max_length = min(len(value)+2, 50)
                res.append(self.genStr(max_length))
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
                    res.append("-100"+unit)
                    res.append("00x")
                    res.append("999999"+unit)
                    res.append("00mb")
        if len(res) == 0:
            p = random.random()
            if p > 0.5:
                res.append("10"+ datasize[0])
            else:
                max_length = min(len(value)+2, 50)
                res.append(self.genStr(max_length))
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