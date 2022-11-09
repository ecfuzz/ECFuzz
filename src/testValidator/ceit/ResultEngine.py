import json

from testValidator.ceit.result_analyzer.result_analyzer import ResultAnalyzer
from testValidator.ceit.ceitutils.file_system_utils import get_files_in_dir

from utils.Configuration import Configuration


class ResultEngine( object ):
    log_engine = None
    data_engine = None
    result_dir = ""
    char2cut = 0
    result_analyzer = None
    oracles = Configuration.putConf['test_oracles_path']
    oracle_dict = {}

    def __init__(self, log_engine, char2cut):
        self.log_engine = log_engine
        self.log_engine.info( "ResultEngine Startup." )
        self.char2cut = char2cut
        self.result_analyzer = ResultAnalyzer()

        with open( self.oracles, 'r' ) as fp1:
            content = fp1.read()
            self.oracle_dict = json.loads( content )

    def set_directory(self, directory):
        self.result_dir = directory

    def build_indexes(self):
        self.result_analyzer.build_documents( self.result_dir, self.oracle_dict )

    def query(self, words):
        for word in words:
            self.overall_results = self.result_analyzer.query( word )
            self.detailed_results = self.result_analyzer.get_detailed_results()

            if self.overall_results == True:
                return True
        return False

    def query_with_baseline(self, words, misconf=None):
        for word in words:
            self.overall_results = self.result_analyzer.query_with_baseline( word, misconf )
            self.detailed_results = self.result_analyzer.get_detailed_results()

            if self.overall_results == True:
                return True
        return False

    def query_with_filter(self, words):
        for word in words:
            self.overall_results = self.result_analyzer.query_with_filter( word)
            self.detailed_results = self.result_analyzer.get_detailed_results()

            if self.overall_results == True:
                return True
        return False

    def get_analyzer_results(self):
        return self.detailed_results

    def build_baseline(self, baseline_dir):
        files = get_files_in_dir( baseline_dir )[baseline_dir]
        self.result_analyzer.set_char2cut( self.char2cut )
        self.result_analyzer.build_baseline( baseline_dir, files)

    def build_indexes_with_baseline(self):
        self.result_analyzer.build_documents_with_baseline( self.result_dir, self.oracle_dict )

