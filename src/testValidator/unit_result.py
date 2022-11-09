class unit_result(object):
    def __init__(self, ran_tests_and_time=set(), failed_tests=set()):
        self.failed_tests = failed_tests
        self.ran_tests_and_time = ran_tests_and_time