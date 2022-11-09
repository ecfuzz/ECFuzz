import os

from dataModel.ConfItem import ConfItem
from dataModel.Seed import Seed
from typing import List

from utils.Configuration import Configuration
import xml.etree.ElementTree as ET

from utils.Logger import getLogger


class Testcase(Seed):
    """
    This is a data model for testcase in configuration fuzzing. 
    """

    def __init__(self, confItems: List[ConfItem] = None) -> None:
        self.logger = getLogger()
        if confItems is None:
            confItems = []
        super().__init__(confItems)
        self.fileDir = Configuration.fuzzerConf['unit_testcase_dir']

    def __str__(self) -> str:
        return "Testcase:\n" + "".join(str(conf) + "\n" for conf in self.confItemList)

    def writeToFile(self, fileName: str = None) -> str:
        if not os.path.exists(self.fileDir):
            os.mkdir(self.fileDir)

        if self.fileName.__len__() == 0:
            if fileName:
                filePath = os.path.join(self.fileDir, fileName)
            else:
                filePath = os.path.join(self.fileDir, self.generateFileName())
        else:
            filePath = os.path.join(self.fileDir, self.fileName)

        self.filePath = filePath
        if Configuration.fuzzerConf['project'] in ["hadoop-common", "hadoop-hdfs", "hbase"]:
            self.filePath = f'{self.filePath}.xml'
            conf = ET.Element("configuration")
            for confItem in self.confItemList:
                p, v = confItem.name, confItem.value
                prop = ET.SubElement(conf, "property")
                name = ET.SubElement(prop, "name")
                value = ET.SubElement(prop, "value")
                name.text = p
                value.text = v
            with open(self.filePath, 'wb') as file:
                file.write(str.encode(
                    "<?xml version=\"1.0\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n"))
                file.write(ET.tostring(conf))
        elif Configuration.fuzzerConf['project'] in ["zookeeper"]:
            self.filePath = f'{self.filePath}.cfg'
            with open(self.filePath, "w") as file:
                for confItem in self.confItemList:
                    p, v = confItem.name, confItem.value
                    file.write(f"{p}={v}" + "\n")
        elif Configuration.fuzzerConf['project'] in ["alluxio"]:
            self.filePath = f'{self.filePath}.properties'
            with open(self.filePath, "w") as file:
                for confItem in self.confItemList:
                    p, v = confItem.name, confItem.value
                    file.write(f"{p}={v}" + "\n")
        else:
            self.logger.info("it doesn't support the given project : ".format(Configuration.fuzzerConf['project']))

        return self.filePath
