import os
import shutil
import stat
import sys
from importlib import reload

from numpy import unicode

from utils.Configuration import Configuration

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from ..ceitutils.file_system_utils import get_file_content, get_rid_of_string
from ..ceitutils.regex_expression_utils import find_pattern, remove_pattern, add_escape
from whoosh.analysis import StemmingAnalyzer
from wordsegment import load, segment


class ResultAnalyzer( object ):
    ix = None
    writer = None
    testcase_ids = []
    overall_results = False
    detailed_results = {}
    baseline = {}
    char2cut = 0

    def __init__(self):
        if not os.path.exists( "index" ):
            os.mkdir( "index" )
        else:
            if not os.access("index", os.W_OK):
                # print(os.getcwd())
                os.chmod("index", stat.S_IWRITE)
            shutil.rmtree( "index" )
            os.mkdir( "index" )
        load()
    def init_index(self):
        if not os.path.exists( "index" ):
            os.mkdir( "index" )
        else:
            if not os.access("index", os.W_OK):
                os.chmod("index", stat.S_IWRITE)
            shutil.rmtree( "index" )
        os.mkdir( "index" )

    def set_char2cut(self, char2cut):
        self.char2cut = char2cut

    def add_document(self, path, title, content):
        self.writer.add_document( title=title, path=path,
                                  content=content )

    def init_whoosh(self):
        schema = Schema( title=TEXT( stored=True ), path=ID( stored=True ), content=TEXT(analyzer=StemmingAnalyzer()))
        self.ix = create_in( "index", schema )
        self.writer = self.ix.writer()

    def commit(self):
        self.writer.commit()

    def queryWithStemming(self, string, content):
        if string in content:
            return True

        words = segment( string )
        for word in words:
            if not word.isalpha():
                words.remove( word )
        string1 = " ".join( words )
        # print string1
        words = segment( string + "s" )
        for word in words:
            if not word.isalpha():
                words.remove( word )
        string2 = " ".join( words )
        # print string2

        self.init_index()
        schema = Schema( title=TEXT( stored=True ), path=ID( stored=True ),
                         content=TEXT( analyzer=StemmingAnalyzer() ) )
        ix = create_in( "index", schema )
        writer = ix.writer()
        # content = "The good pid file  function of directory good can not work"
        writer.add_document( title=u"First document", path=u"/a", content=unicode( content ) )
        writer.commit()
        with ix.searcher() as searcher:
            query = QueryParser( "content", ix.schema ).parse( string1 )
            results = searcher.search( query )
            res1 = len( results ) > 0

            query = QueryParser( "content", ix.schema ).parse( string2 )
            results = searcher.search( query )
            res2 = len( results ) > 0
        res = res1 | res2
        # print res, res1, res2
        return res

    def query(self, string):
        #split the words and make sure they can both appear in the context

        string = string.lower()
        self.detailed_results = {}
        self.overall_results = False
        for testcase_id in self.testcase_ids:
            with open( testcase_id["path"], 'r' ) as fp:
                content = fp.read()
                content = self.formalize_contents( content )
                res = self.queryWithStemming( string, content )
                if res == True:
                    self.detailed_results[testcase_id["testcase_id"]] = True
                    self.overall_results = True

                else:
                    if self.detailed_results.has_key( testcase_id["testcase_id"] ):
                        pass
                    else:
                        self.detailed_results[testcase_id["testcase_id"]] = False

        return self.overall_results

    def get_files(self, directory):
        files = []
        for i in os.walk( directory ):
            directory = i[0]
            filenames = i[2]
            for filename in filenames:
                fullname = directory + os.sep + filename
                files.append( fullname )
        return files

    def build_documents(self, directory, oracle_dict):

        self.testcase_ids = []

        files = self.get_files( directory )
        if Configuration.putConf['test_mode'] == "Default":
            for file in files:
                path = file
                title = file.split( '/' )[-1]
                if ".txt" in title:
                    testcase_id = title.split( "_" )[0]
                    if oracle_dict[testcase_id]["ignored"] == False:
                        self.testcase_ids.append( {
                            "testcase_id": testcase_id,
                            "path": path,
                            "title": title,
                            "log2annotate": oracle_dict[testcase_id]["log2annotate"],
                            "log2purge": oracle_dict[testcase_id]["log2purge"],
                        } )
        else:
            print("unknown test mode!")

            #     with open( file, 'r' ) as fp:
            #         content = fp.read()
            #         content = self.formalize_contents( char2cut, content )
            #     self.add_document( unicode( path ), unicode( title ), unicode( content ) )
            # else:
            #     pass

    def formalize_contents(self, file_content):
        newSentences = []
        sentences = file_content.split( '\n' )
        for sentence in sentences:
            sentence = sentence[self.char2cut:]
            newSentences.append( sentence )
        file_content = '\n'.join( newSentences )
        rstr = r"[-,.\/\\\:\*\?\"\<\>\|]"
        new_content = re.sub( rstr, " ", file_content )
        rstr = r"[\[\]~\(\)\{\}\'\"=\_#+]"
        new_content = re.sub( rstr, " ", new_content )
        new_content = new_content.lower()
        return new_content

    def get_detailed_results(self):
        return self.detailed_results

    def build_baseline(self, directory, files):
        for file in files:
            file_path = directory + '/' + file
            file_content = get_file_content( file_path )
            self.baseline[file] = self.formalize_contents_with_baseline( file_content )

    def formalize_contents_with_baseline(self, file_content):
        content = self.formalize_contents( file_content )
        rstr = r"[1234567890]"
        newcontent = re.sub( rstr, " ", content )
        content_list = newcontent.split( '\n' )
        new_content_list = []
        for line in content_list:
            line = " ".join( line.split() )
            new_content_list.append( line )
        return new_content_list

    def formalize_contents_with_filter(self, file_content, log2annotate=[""], log2purge=[""]):
        content_list = file_content.split( '\n' )
        new_content_list = []
        for line in content_list:
            ignored_flag = False
            for pattern in log2annotate:

                pattern = add_escape( pattern )

                if find_pattern( line, pattern ):
                    ignored_flag = True
                #if pattern == "ah00561: request header exceeds limitrequestfieldsize:" and "ah00561: request header" in line:
                    #print "Result of find pattern:", find_pattern( line, pattern )
                    #print line
            if ignored_flag == False:
                for pattern in log2purge:
                    pattern = add_escape( pattern )
                    line = remove_pattern( line, pattern )
                line = " ".join( line.split() )
                new_content_list.append( line )
        new_file_content = '\n'.join( new_content_list )
        new_file_content = new_file_content.lower()
        return new_file_content

    def build_documents_with_baseline(self, directory, oracle_dict):

        self.testcase_ids = []

        files = self.get_files( directory )
        for file in files:
            path = file
            title = file.split( '/' )[-1]
            testcase_id = title.split( "_" )[0]
            if oracle_dict[testcase_id]["ignored"] == False:
                self.testcase_ids.append( {
                    "testcase_id": testcase_id,
                    "path": path,
                    "title": title,
                    "log2annotate": oracle_dict[testcase_id]["log2annotate"],
                    "log2purge": oracle_dict[testcase_id]["log2purge"],
                } )

    def query_with_baseline(self, string, misconf=None):
        string = self.formalize_contents_with_baseline( string )[0]
        string = "*" + string + "*"
        print("string is \n")
        print(string)
        self.detailed_results = {}
        self.overall_results = False
        for testcase_id in self.testcase_ids:
            self.init_whoosh()
            with open( testcase_id["path"], 'r' ) as fp:
                content = fp.read()
                content = self.get_relevant_logs( testcase_id["title"], content, misconf )
                print("content is : \n")
                print(content)
                self.add_document( unicode( testcase_id["path"] ), unicode( testcase_id["title"] ), unicode( content ) )
                self.commit()
                string = string.lower()
                with self.ix.searcher() as searcher:
                    query = QueryParser( "content", self.ix.schema ).parse( string )
                    results = searcher.search( query )
                    if results.__len__() != 0:
                        self.detailed_results[testcase_id["testcase_id"]] = True
                        self.overall_results = True

                    else:
                        if self.detailed_results.has_key( testcase_id["testcase_id"] ):
                            pass
                        else:
                            self.detailed_results[testcase_id["testcase_id"]] = False

        return self.overall_results

    def query_with_filter(self, string):
        string = string.lower()
        """
        string = "*" + string + "*"
        """
        self.detailed_results = {}
        self.overall_results = False
        for testcase_id in self.testcase_ids:
            # self.init_whoosh()

            log2annotate_patterns = testcase_id["log2annotate"]
            log2purge_patterns = testcase_id["log2purge"]
            with open( testcase_id["path"], 'r' ) as fp:
                """
                content = fp.read()
                content = self.formalize_contents_with_filter( content,  log2annotate_patterns, log2purge_patterns)
                self.add_document( unicode( testcase_id["path"] ), unicode(  ), unicode( content ) )
                self.commit()
                with self.ix.searcher() as searcher:
                    print string
                    query = QueryParser( "content", self.ix.schema ).parse( string )
                    results = searcher.search( query )
                    print results
                """
                content = fp.read()
                content = self.formalize_contents_with_filter( content, log2annotate_patterns, log2purge_patterns )
                content = content.lower()
                if string in content:
                    self.detailed_results[testcase_id["testcase_id"]] = True
                    self.overall_results = True

                else:
                    if self.detailed_results.has_key( testcase_id["testcase_id"] ):
                        pass
                    else:
                        self.detailed_results[testcase_id["testcase_id"]] = False
                """
                    if results.__len__() != 0:
                        self.detailed_results[testcase_id["testcase_id"]] = True
                        self.overall_results = True

                    else:
                        if self.detailed_results.has_key( testcase_id["testcase_id"] ):
                            pass
                        else:
                            self.detailed_results[testcase_id["testcase_id"]] = False
                """

        return self.overall_results

    def get_relevant_logs(self, file_name, content, misconf):
        relevant_logs = []
        if misconf != None:
            content = get_rid_of_string( content, misconf )
        content_list = self.formalize_contents_with_baseline( content )
        baseline_content_list = self.baseline[file_name]
        for sentence in content_list:
            flag = False
            for base_sentence in baseline_content_list:
                if sentence in base_sentence:
                    flag = True
                else:
                    pass

            if not flag:
                relevant_logs.append( sentence )
            else:
                pass

        relevant_logs = "\n".join( relevant_logs )

        return relevant_logs


def main():
    a = ResultAnalyzer()
    a.init_whoosh()
    a.add_document(u"/1", u"title1", u"content1")
    a.add_document(u"/2", u"title2", u"content2")
    a.commit()
    b = a.query(u"content")
    print(b)
    # print a.get_files("../MisconfGenerator")
    #a.set_char2cut( 0 )
    #a.build_baseline( "/Users/Leo/Desktop/ceitinspector/ceitinspector/core/Log", ["2018-11-02-104220.log"], [] )
    #file_name = "2018-11-02-104220.log"
    content = """
2018/11/05 16:14:14.840| 0,9| debug.cc(408) parseOptions: command-line -X overrides: ALL,7
2018/11/05 16:14:14.840| 16,3| cache_manager.cc(80) registerProfile: registering legacy mem
2018/11/05 16:14:14.840| 16,5| cache_manager.cc(114) findAction: CacheManager::findAction: looking for action mem
2018/11/05 16:14:14.840| 16,6| cache_manager.cc(122) findAction: Action not found.
2018/11/05 16:14:14.840| 16,3| cache_manager.cc(65) registerProfile: registered profile: mem
2018/11/05 16:14:14.840| 16,5| cache_manager.cc(114) findAction: CacheManager::findAction: looking for action diskd
2018/11/05 16:14:14.840| 16,6| cache_manager.cc(122) findAction: Action not found.
2018/11/05 16:14:14.840| 16,3| cache_manager.cc(65) registerProfile: registered profile: diskd
2018/11/05 16:14:14.840| 16,3| cache_manager.cc(80) registerProfile: registering legacy squidaio_counts
2018/11/05 16:14:14.840| 16,5| cache_manager.cc(114) findAction: CacheManager::findAction: looking for action squidaio_counts
2018/11/05 16:14:14.840| 16,6| cache_manager.cc(122) findAction: Action not found.
maybe i can find it 388
2018/11/05 16:14:14.840| 16,3| cache_manager.cc(65) registerProfile: registered profile: squidaio_counts
2018/11/05 16:14:14.840| 92,2| rock/RockStoreFileSystem.cc(50) setup: Will use Rock FS
perhaps you 244 are right
2018/11/05 16:14:14.840| Startup: Initializing Authentication Schemes ...
2018/11/05 16:14:14.840| Startup: Initialized Authentication Scheme 'basic'
2018/11/05 16:14:14.840| Startup: Initialized Authentication Scheme 'digest'
2018/11/05 16:14:14.840| Startup: Initialized Authentication Scheme 'negotiate'
2018/11/05 16:14:14.840| Startup: Initialized Authentication Scheme 'ntlm'
2018/11/05 yes i can do it #yes+
"""
    #b = a.get_relevant_logs( file_name, content, "yes" )
    #print b

    #print a.formalize_contents_with_baseline( "icon_directory" )[0]


    #print words
if __name__ == "__main__":
    main()
