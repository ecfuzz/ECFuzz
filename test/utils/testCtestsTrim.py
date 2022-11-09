import unittest, sys

sys.path.append("../../src/")

from utils.TimeFilterTrimmer import TimeFilterTrimmer
from utils.SampleTrimmer import SampleTrimmer
from utils.Configuration import Configuration
from utils.ConfAnalyzer import ConfAnalyzer

class testCtestsTrim(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("start to test class `testCtestsTrim`")
        Configuration.parseConfiguration()
        ConfAnalyzer.analyzeConfItems()

    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'testCtestsTrim'")

    def testLoad(self) -> None:
        TF = TimeFilterTrimmer()
        ST = SampleTrimmer()
        res = TF.trimCtests(ConfAnalyzer.confUnitMap)
        print(res)
        print(ST.trimCtests(res))

if __name__ == "__main__":
    unittest.main()
