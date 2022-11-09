from utils.Kmeans import Kmeans

class ClassifyConfItems(object):

    def __init__(self) -> None:
        pass

    def run(self, conItems: dict, mapping: dict):
        """
       
       
        
        
        
        """
        # conItems = ConfAnalyzer.confItemValueMap
        ctest_data = {}
        # mapping = ConfAnalyzer.confUnitMap
        for conf in conItems:
            if conf in mapping:
                ctest_data[conf] = mapping[conf]
        # print("ctest_data:", ctest_data)
        # print(">>>>conf_has_tests_count:%s,conf_has_not_tests_count:%s" %(len(ctest_data),len(conItems)-len(ctest_data)))
        
        sorted_ctest_data = sorted(ctest_data.items(), key=lambda x:len(x[1]), reverse=True)
        # print(sorted_ctest_data)
        # for x in sorted_ctest_data:
        #     print(x[0], ":", len(x[1]))
        baseConf_len = 0
        baseConf = set()
        mutableConf = set()
        all_conf_len = []
        for x in sorted_ctest_data:
            tmp_conf_len = []
            tmp_conf_len.append(len(x[1]))
            all_conf_len.append(tmp_conf_len)
            
            # BASECONF_THRESHOLD = 2000
            # if len(x[1]) > BASECONF_THRESHOLD:
            #     baseConf.add(x[0])
            # else:
            #     mutableConf.add(x[0])

        
        kmeans = Kmeans(all_conf_len, 2)
        assignment, _ = kmeans.k_means()
        if (assignment[0] == 0):
            baseConf_len = len(assignment) - sum(assignment)
        elif (assignment[0] == 1):
            baseConf_len = sum(assignment)
        else:
            raise Exception("Keans error")

        tmp_count = 0
        for x in sorted_ctest_data:
            tmp_count += 1
            if tmp_count <= baseConf_len:
                baseConf.add(x[0])
            else:
                mutableConf.add(x[0])
        # print("BaseConf:", len(baseConf))
        # print("MutableConf:", len(mutableConf))
        return list(baseConf), list(mutableConf)

