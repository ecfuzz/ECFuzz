import re
import xml.etree.ElementTree as ET
from typing import Dict

from utils.IdentifyType import IdentifyType
from utils.Configuration import Configuration
from utils.Logger import getLogger

class ConfParser(object):
    """parse the conf based the specified project

    Args:
        object : None
    """

    def __init__(self) -> None:
        self.project: str = Configuration.fuzzerConf['project']
        self.path: str = Configuration.putConf['conf_path']
        self.deprecate_conf : dict = self.load_deprecate_config_map()
        self.logger = getLogger()

    def load_deprecate_config_map(self) -> Dict:
        """ 
        some project has deprecate configuration
        , deprecate config are config names refactored to a new config name,
        make sure to put them in a file, formatted as `deprecate param, new param`
        and add the file path to DEPRECATE_CONF_FILE in constant.py
        """
        deprecate_conf = {}  # load deprecate map
        if self.project in ["hadoop-hdfs", "hadoop-common"]:
            with open(Configuration.putConf['deprecate_conf_path']) as conf_file:
                for line in conf_file:
                    deprecate_param, param = line.strip("\n").split("\t")
                    deprecate_conf[deprecate_param] = param
        return deprecate_conf

    def parse_conf_file(self) -> Dict:
        """parse conf file, the unified call

        Args:
            path (str): the path needs to be parsed

        Returns:
            dict : a map of key, value for the given conf path
        """
        confItemValueMap = {}
        if self.project in ["hadoop-common", "hadoop-hdfs", "hbase"]:
            confItemValueMap = self.parse_conf_file_xml()
        elif self.project in ["zookeeper", "alluxio"]:
            confItemValueMap = self.parse_conf_file_properties()
        else:
            return {}, {}
            
        confItemTypeMap = {}
        for confName in confItemValueMap:
            confValue = confItemValueMap[confName]
            confType = IdentifyType().run(confName, confValue)
            confItemTypeMap[confName] = confType

        for key in confItemValueMap.keys():
            if confItemValueMap[key] is None:
                confItemValueMap[key] = ''

        return confItemValueMap, confItemTypeMap
        
    def parse_conf_file_xml(self) -> dict:
        """parse xml path

        Args:
            path (str): conf file path

        Returns:
            dict: conf name, conf value. it will also save the None value
        """
        deprecate_conf = self.deprecate_conf
        conf_map = {}
        fd = ET.parse(self.path)
        for kv in fd.getroot():
            # get key value pair
            cur_value = ''
            cur_key = ''
            for prop in kv:
                if prop.tag == "name":
                    cur_key = re.sub('\n|\t', '', re.sub(' +', ' ', prop.text))
                elif prop.tag == "value" and cur_key:
                    cur_value = prop.text
            if cur_key not in conf_map:
                if cur_key in deprecate_conf:
                    self.logger.info(">>>>[ConfParser] {} in your input conf file is deprecated in the project,".format(cur_key)
                          + " replaced with {}".format(deprecate_conf[cur_key]))
                    cur_key = deprecate_conf[cur_key]
                conf_map[cur_key] = cur_value
        return conf_map

    def parse_conf_file_properties(self) -> dict:
        """parse property path

        Args:
            path (str): conf file path

        Returns:
            dict: pairs of conf name and conf value
        """
        deprecate_conf = self.deprecate_conf
        conf_map = {}
        with open(self.path) as p_file:
            for line in p_file:
                if line.startswith("#"):
                    continue
                seg = line.strip("\n").split("=")
                if len(seg) == 2:
                    cur_key, cur_value = [x.strip() for x in seg]
                    if cur_key not in conf_map:
                        if cur_key in deprecate_conf:
                            self.logger.info(
                                ">>>>[ConfParser] {} in your input conf file is deprecated in the project,".format(cur_key)
                                + " replaced with {}".format(deprecate_conf[cur_key]))
                            cur_key = deprecate_conf[cur_key]
                        conf_map[cur_key] = cur_value
        return conf_map
