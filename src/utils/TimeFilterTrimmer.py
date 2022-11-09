import operator
from typing import Dict, List
import pandas as pd

from utils.Logger import getLogger
from utils.TrimCtestsInterface import TrimCtestsInterface
from utils.Configuration import Configuration


class TimeFilterTrimmer(TrimCtestsInterface):
    """trim tests by it's running time

    Args:
        TrimCtestsInterface (_type_): interface of ctests trimmer
    """

    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger()
        self.data = self.loadTimeInfo()
        self.scale = float(Configuration.fuzzerConf['ctests_trim_scale'])  # save scale

    def loadTimeInfo(self) -> dict:
        """load testcase time, note that tsv would not contain testcase in json file.
        and json file would not contain testcase in tsv file.
        it just needs to be loaded once.

        Returns:
            dict: testcase and it's time of each pair
        """
        dp = pd.read_csv(Configuration.putConf['tests_time_path'], sep='\t',
                         names=["confname", "time1", "time2", "time3", "time4", "time5"])
        size = dp.shape[0]
        data = {dp.loc[i][0]: sum(dp.loc[i][1:6]) / 5 for i in range(size)}
        return dict(sorted(data.items(), key=operator.itemgetter(1)))

    def trimCtests(self, tests_map: dict, data: dict) -> Dict[str, List[str]]:
        self.logger.info("start to trim ctests by time!")
        new_map = {}
        for conf, tests in tests_map.items():
            # tmp = {test: data[test] for test in tests if test in data}
            # sorted_tmp = dict(sorted(tmp.items(), key=operator.itemgetter(1)))
            # new_map[conf] = [test for test in tests if (test in data and data[test] < 10)]
            # for test in tests:
            #     if data[test] > 10:
            #         continue
            #     else :
            #         new_map[conf]
            new_map[conf] = []
            for test in tests:
                if test in data:
                    if data[test] < 5:
                        new_map[conf].append(test)
                    else:
                        continue
                else:
                    new_map[conf].append(test)
            # ls = list(sorted_tmp.keys())
            # leaved = (int)(len(ls) * self.scale)
            # new_map[conf] = [ls[0]] if leaved < 1 else ls[:leaved]
        self.logger.info("trim by time done!")
        return new_map
