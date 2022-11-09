from testValidator.ceit.data_recorder.data_recorder import DataRecorder
from testValidator.ceit.data_recorder.data_structure import RedisDataKey, RedisDataValue


class DataEngine( object ):
    log_engine = None
    data_recorder = None
    prefix = ""
    redis_data_key = None
    name = ""
    key = ""
    misconf = ""
    mutation_type = ""
    value = {}
    test_case_num = 0

    def __init__(self, log_engine, prefix):
        self.log_engine = log_engine
        self.log_engine.info( "DataEngine Startup." )
        self.data_recorder = DataRecorder()
        self.prefix = prefix
        self.clean_all()

    def set_name(self, option_name):
        self.redis_data_key = RedisDataKey( prefix=self.prefix )
        self.name = self.redis_data_key( option_name )

    def set_key(self, mutant_name):
        self.key = mutant_name

    def has_name_and_key(self):
        if self.key in self.data_recorder.get_keys( self.name ):
            return True
        else:
            return False

    def set_misconf(self, misconf):
        self.misconf = misconf

    def set_mutation_type(self, mutation_type):
        self.mutation_type = mutation_type

    def init_value(self):
        self.value = RedisDataValue( self.mutation_type, self.key, self.misconf, self.test_case_num )

    def set_testcase_results_fail(self, id):
        self.value.set_testcase_results_fail( id )

    def load_value(self):
        if self.has_name_and_key():
            value = self.data_recorder.get_value_from_key( name=self.name, key=self.key )
            self.value = self.value( value )
            # print self.value()

    def flush(self):
        self.data_recorder.insert( self.name, self.key, self.value() )

    def set_test_case_num(self, len):
        self.test_case_num = len

    def set_analyzer_results(self, detailed_results):
        for id in detailed_results:
            if detailed_results[id] == True:
                self.set_analyzer_results_good( id )

    def set_observer_results(self, detailed_results):
        crash_results, hang_results, termination_results = detailed_results
        for i in range( self.test_case_num ):
            id = str( i + 1 )
            if crash_results[id] == True:
                self.set_observer_results_crash_true(id)
            elif hang_results[id] == True:
                self.set_observer_results_hang_true(id)
            elif termination_results[id] == True:
                self.set_observer_results_termination_true(id)
            else:
                pass

    def set_observer_results_crash_true(self, id):
        self.value.set_observer_results_crash_true(id)

    def set_observer_results_hang_true(self, id):
        self.value.set_observer_results_hang_true(id)

    def set_observer_results_termination_true(self, id):
        self.value.set_observer_results_termination_true(id)

    def set_analyzer_results_good(self, id):
        self.value.set_analyzer_results_good( id )

    def show_all(self, option_name):
        name = self.redis_data_key( option_name )
        return self.data_recorder.get_all_value_from_name( name )

    def show_overall_results(self, option_name, mutant_name):
        name = self.redis_data_key(option_name)
        value = self.data_recorder.get_value_from_key( name, mutant_name )
        self.value = self.value(value)
        return self.value.overall_results()

    def dump_overall_results(self, file_path):
        self.data_recorder.dump_overall_results(file_path)


    def clean_all(self):
        self.data_recorder.clean()
