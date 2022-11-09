import random
from typing import Dict, List

from utils.Logger import getLogger
from utils.TrimCtestsInterface import TrimCtestsInterface
from utils.Configuration import Configuration

class SampleTrimmer(TrimCtestsInterface):
    """trim tests by sampling the tests

    Args:
        TrimCtestsInterface (_type_): interface of ctests trimmer
    """
    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger()
        self.sampling = int(Configuration.fuzzerConf['ctests_trim_sampling'])
    
    def trimCtests(self, tests_map: dict) -> Dict[str, List[str]]:
        self.logger.info("start to trim ctests by sampling!")
        new_map = {}
        for conf, tests in tests_map.items():
            random.shuffle(tests)
            lens = len(tests)
            if lens <= self.sampling:
                new_map[conf] = tests
            else:
                new_map[conf] = [tests[index] for index in range(0,lens,self.sampling)]
        self.logger.info("trim by sampling done!")
        return new_map
