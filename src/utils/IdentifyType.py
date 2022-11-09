import re

NONE = "NOTYPE"
INT = "INT"
FLOAT = "FLOAT"
BOOL = "BOOL"
FILEPATH = "FILEPATH"
IP = "IP"
PORT = "PORT"
IPPORT = "IPPORT"
CLASSNAME = "CLASSNAME"
DIRPATH = "DIRPATH"
INTLIST = "INTLIST"
STRLIST = "STRLIST"
TIME = "TIME"
DATA = "DATA"
PM = "PM"
PC = "PC"
ZKDIR = "ZKDIR"
ZKPORT = "ZKPORT"
ZKPORTADDRESS = "ZKPORTADDRESS"
ZKLIMIT = "ZKLIMIT"
ZKSIZE = "ZKSIZE"
ALGO = "ALGORITHM"
USER = "USER"
GROUP = "GROUP"
NAMESERVICES = "NAMESERVICES"
INTERFACE = "INTERFACE"
POTENTIALFLOAT = "POTENTIALFLOAT"


class IdentifyType(object):
    def __init__(self) -> None:
        pass

    # guess from value
    def isBool(self, s):
        if s.lower() == "true" or s.lower() == "false":
            return True
        else:
            return False

    def isPort(self, name, value):
        if value == "" and name.endswith(".port"):
            return True
        if self.isInt(value) and name.endswith(".port"):
            return True
        return False

    def isPermissionMask(self, name, value):
        if len(value) == 3 and "umask" in name:
            try:
                _ = int("0o" + value, base=8)
                return True
            except ValueError:
                return False

    def isPermissionCode(self, s):
        if len(s) == 9:
            m = re.match(r"^[rwx]+$", s)
            if m:
                return True
        return False

    def isInt(self, s):
        try:
            _ = int(s)
            return True
        except ValueError:
            return False

    def isFloat(self, s):
        m = re.match(r"^\d+\.\d+[fF]$", s)
        if m:
            s = s[:-1]
        try:
            _ = float(s)
            return True
        except ValueError:
            return False

    def isIpAddr(self, s):
        m = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", s)
        return m is not None

    def isIpPortAddr(self, s):
        m = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$", s)
        return m is not None

    def isClassName(self, s):
        return s.startswith("org.apache.hadoop") or s.startswith("alluxio.")

    def isFilePath(self, s):
        # extend, ${} and "/" in dvalue
        if re.match(r"\$\{.*\}", s) and "/" in s:
            return True
        elif s.startswith("/"):
            return True
        else:
            return False

    def isIntList(self, s):
        elements = s.split(",")
        res = True
        for ele in elements:
            res &= self.isInt(ele)
        return res

    def isStringList(self, s):
        return s.count(",") > 0

    def isTime(self, s):
        timeunits = ["ms", "millisecond", "s", "sec", "second", "m", "min", "minute", "h", "hr", "hour", "d", "day"]
        for unit in timeunits:
            if s.endswith(unit):
                t = s[:s.find(unit)]
                if self.isInt(t):
                    return True
        return False

    def isDataSize(self, s):
        datasize = ["MB"]
        for unit in datasize:
            if s.endswith(unit):
                t = s[:s.find(unit)]
                if self.isInt(t):
                    return True
        return False

    def isAlgorithm(self, s):
        return s.endswith(".algorithm")

    # guess from name
    def isFilePath2(self, name):
        return name.endswith(".conf") or name.endswith('.path')

    def isFilePath3(self, name):
        return name.endswith(".file") or name.endswith(".file.name") or name.endswith("keytab")

    def isDirPath(self, name):
        return name.endswith(".dir")

    def isAddr(self, name):
        return name.endswith(".addr") or name.endswith(".addresses") or name.endswith(".hostname") or name.endswith(
            "address")

    def isClassName2(self, name):
        return name.endswith(".class") or name.endswith(".classes")

    def isUser(self, name):
        return name.endswith("user") or name.endswith("users")

    def isGroup(self, name):
        return name.endswith("group") or name.endswith("groups")

    def isNameservices(self, name):
        return name.endswith("nameservices")

    def isInterface(self, name):
        return name.endswith("interface") or name.endswith("interfaces")

    def isPotentialFloat(self, name):
        return name.endswith("limit") or name.endswith("size")

    def run(self, name, value):
        # return type
        # guess from value
        if value == None:
            return ''
        if self.isBool(value):
            return BOOL
        if self.isPort(name, value):
            return PORT
        if self.isPermissionMask(name, value):
            return PM
        if self.isInt(value):
            return INT
        if self.isFloat(value):
            return FLOAT
        if self.isPermissionCode(value):
            return PC
        if self.isIntList(value):
            return INTLIST
        if self.isStringList(value):
            return STRLIST
        if self.isIpAddr(value):
            return IP
        if self.isIpPortAddr(value):
            return IPPORT
        if self.isClassName(value):
            return CLASSNAME
        if self.isFilePath(value):
            return FILEPATH
        if self.isTime(value):
            return TIME
        if self.isDataSize(value):
            return DATA
        # guess from name
        if self.isDirPath(name):
            return DIRPATH
        if self.isAddr(name):
            return IP
        if self.isClassName2(name):
            return CLASSNAME
        if self.isFilePath2(name):
            return FILEPATH
        if self.isFilePath3(name):
            return FILEPATH
        if self.isAlgorithm(name):
            return ALGO
        if self.isUser(name):
            return USER
        if self.isGroup(name):
            return GROUP
        if self.isNameservices(name):
            return NAMESERVICES
        if self.isInterface(name):
            return INTERFACE
        # else:
        #     return None
