import configparser
import os.path
import typing
from typing import Dict, Any

from utils.UnitConstant import FUZZER_DIR, ROOT_DIR


class Configuration(object):
    """
    A class to parse and obtains configurations about fuzzing meta data.

    Attributes:
        Configuration.configuration (dict): a dictionary that stores different configurations about fuzzing meta data.
    """

    configuration: Dict[str, Dict[str, str]]
    fuzzerConf: Dict[str,str]
    putConf: Dict[str,str]

    @staticmethod
    def parseConfiguration() -> None:
        cf = configparser.ConfigParser()
        cf.read(os.path.join(FUZZER_DIR, "fuzzing.conf"))

        sections: Dict[str, Dict[str, Any]] \
                    = {section_key: dict(cf.items(section_key)) for section_key in cf.sections()}

        for section in sections.values():
            for key, value in section.items():
                # 只转换路径变量
                if "path" in key or "dir" in key:
                    section[key] = os.path.join(ROOT_DIR, value)
                elif value.startswith('['):
                    section[key] = value[1:][:-1].strip().split(',')

        Configuration.configuration = sections
        Configuration.fuzzerConf = sections['fuzzer']

        project = sections['fuzzer']['project']
        putConfPath = sections[project]['file_path']

        cf = configparser.ConfigParser()
        cf.read(putConfPath)

        section = {section_key: dict(cf.items(section_key)) for section_key in cf.sections()}[project]

        for key, value in section.items():
            if "path" in key or "dir" in key:
                section[key] = os.path.join(ROOT_DIR, value)
            elif value.startswith('['):
                section[key] = [os.path.join(ROOT_DIR, elem) for elem in value[1:][:-1].strip().split(',')]

        Configuration.putConf = section
