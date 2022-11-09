import json
from copy import deepcopy


class RedisDataKey( object ):
    def __init__(self, prefix, ex=None):
        self.prefix = prefix
        self.ex = ex

    def __call__(self, key):
        return self.prefix + ":" + str( key )


class RedisDataValue( object ):
    def __init__(self, mutation_type = "", mutation_name = "", misconf = "", test_case_num = 0):
        self.mutation_type = mutation_type
        self.mutation_name = mutation_name
        self.misconf = misconf
        self.test_case_num = test_case_num
        self.detailed_results = DetailedResults( self.test_case_num )
        self.overall_results = OverallResults()

    def set_testcase_results_fail(self, id):
        self.detailed_results.set_testcase_results_fail( id )
        self.overall_results.set_testcase_results_fail()

    def set_analyzer_results_good(self, id):
        self.detailed_results.set_analyzer_results_good( id )
        self.overall_results.set_analyzer_results_good()

    def set_observer_results_crash_true(self, id):
        self.detailed_results.set_obserber_results_crash_true( id )
        self.overall_results.set_observer_results_crash_true()

    def set_observer_results_hang_true(self, id):
        self.detailed_results.set_obserber_results_hang_true( id )
        self.overall_results.set_observer_results_hang_true()

    def set_observer_results_termination_true(self, id):
        self.detailed_results.set_obserber_results_termination_true( id )
        self.overall_results.set_observer_results_termination_true()

    def reload(self, value_dict):
        self.mutation_type = value_dict["mutation_type"]
        self.mutation_name = value_dict["mutation_name"]
        self.misconf = value_dict["misconf"]
        self.detailed_results = self.detailed_results( value_dict["detailed_results"] )
        self.overall_results = self.overall_results( value_dict["overall_results"] )

    def __call__(self, string2json=None):
        if string2json:
            string2json = string2json.replace( "'", '"' ).replace( 'u"', '"' ).replace( "False", "false" ).replace(
                "True", "true" )
            value_dict = json.loads( string2json )
            self.reload( value_dict )
            return self

        else:
            value = {
                "mutation_type": self.mutation_type,
                "mutation_name": self.mutation_name,
                "misconf": self.misconf,
                "detailed_results": self.detailed_results(),
                "overall_results": self.overall_results()
            }
            return value


class DetailedResults( object ):
    def __init__(self, test_case_num):
        self.testcase_results = TestcaseResults( test_case_num )
        self.analyzer_results = AnalyzerResults( test_case_num )
        self.observer_results = ObserverResults( test_case_num )

    def get_testcase_results(self, testcase_results):
        self.testcase_results = deepcopy( testcase_results )

    def get_analyzer_results(self, analyzer_results):
        self.analyzer_results = deepcopy( analyzer_results )

    def get_observer_results(self, observer_results):
        self.analyzer_results = deepcopy( observer_results )

    def set_testcase_results_fail(self, id):
        self.testcase_results.set_fail( id )

    def set_analyzer_results_good(self, id):
        self.analyzer_results.set_Good( id )

    def set_obserber_results_crash_true(self, id):
        self.observer_results.set_crash_true( id )

    def set_obserber_results_hang_true(self, id):
        self.observer_results.set_hang_true( id )

    def set_obserber_results_termination_true(self, id):
        self.observer_results.set_termination_true( id )

    def reload(self, value_dict):
        self.testcase_results = self.testcase_results( value_dict["testcase_results"] )
        self.observer_results = self.observer_results( value_dict["observer_results"] )
        self.analyzer_results = self.analyzer_results( value_dict["analyzer_results"] )

    def __call__(self, value_dict=None):
        if value_dict:
            self.reload( value_dict )
            return self

        detailed_results = {
            "testcase_results": deepcopy( self.testcase_results() ),
            "analyzer_results": deepcopy( self.analyzer_results() ),
            "observer_results": deepcopy( self.observer_results() )
        }
        return detailed_results


class TestcaseResults( object ):
    def __init__(self, test_case_num):
        self.results = {}
        self.test_case_num = test_case_num
        for i in range( self.test_case_num ):
            id = str( i + 1 )
            self.results[id] = "Pass"

    def set_fail(self, id):
        self.results[id] = "Fail"

    def reload(self, testcase_results):
        temp = deepcopy( testcase_results )
        self.results = temp

    def __call__(self, dict_value=None):
        if dict_value:
            testcase_results = deepcopy( dict_value )
            self.reload( testcase_results )
            return self

        else:
            testcase_results = deepcopy( self.results )
            return testcase_results


class AnalyzerResults( object ):
    def __init__(self, test_case_num):
        self.results = {}
        self.test_case_num = test_case_num
        for i in range( self.test_case_num ):
            id = str( i + 1 )
            self.results[id] = "Bad"

    def set_Good(self, id):
        self.results[id] = "Good"

    def reload(self, analyzer_results):
        temp = deepcopy( analyzer_results )
        self.results = temp

    def __call__(self, dict_value=None):
        if dict_value:
            analyzer_results = deepcopy( dict_value )
            self.reload( analyzer_results )
            return self

        else:
            analyzer_results = deepcopy( self.results )
            return analyzer_results


class ObserverResults( object ):
    def __init__(self, test_case_num):
        self.test_case_num = test_case_num
        self.results = {}
        for i in range( self.test_case_num ):
            id = str( i + 1 )
            self.results[id] = {
                "crash": False,
                "hang": False,
                "termination": False
            }

    def reload(self, observer_results):
        temp = deepcopy( observer_results )
        self.results = temp

    def set_crash_true(self, id):
        self.results[id]["crash"] = True

    def set_hang_true(self, id):
        self.results[id]["hang"] = True

    def set_termination_true(self, id):
        self.results[id]["termination"] = True

    def __call__(self, dict_value=None):

        if dict_value:
            observer_results = deepcopy( dict_value )
            self.reload( observer_results )
            return self

        else:
            observer_results = deepcopy( self.results )
            return observer_results


class OverallResults( object ):
    def __init__(self):
        self.results = {"testcase_results": "Pass",
                        "analyzer_results": "Bad",
                        "observer_results": {
                            "crash": False,
                            "hang": False,
                            "termination": False
                        }}

    def set_testcase_results_fail(self):
        self.results["testcase_results"] = "Fail"

    def set_analyzer_results_good(self):
        self.results["analyzer_results"] = "Good"

    def reload(self, overall_results):
        temp = deepcopy( overall_results )
        self.results = temp

    def set_observer_results_crash_true(self):
        self.results["observer_results"]["crash"] = True

    def set_observer_results_hang_true(self):
        self.results["observer_results"]["hang"] = True

    def set_observer_results_termination_true(self):
        self.results["observer_results"]["termination"] = True

    def __call__(self, dict_value=None):

        if dict_value:
            overall_results = deepcopy( dict_value )
            self.reload( overall_results )
            return self
        else:
            overall_results = deepcopy( self.results )
            return overall_results


def main():
    rdk = RedisDataKey( prefix="squid:" )
    print(rdk( "Listen" ))

    rdv = RedisDataValue( mutation_type="ConfErr", mutation_name="omission", misconf="helloworld" )
    dr = DetailedResults()
    print(rdv())


if __name__ == '__main__':
    main()
