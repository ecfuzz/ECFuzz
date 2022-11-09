import os
import sys
import unittest

from utils.Configuration import Configuration

sys.path.append("../../src")

from dataModel.Seed import Seed
from dataModel.Testcase import Testcase
from dataModel.TestResult import TestResult


class TestWriteToFile(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        Configuration.parseConfiguration()
        self.targetObjects = [Seed(), Testcase(), TestResult()]

    @classmethod
    def setUpClass(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        print("finished testing class 'Seed'")

    def testGenerateFileName(self) -> None:
        for obj in self.targetObjects:
            print(obj.generateFileName())

    def test__str__(self) -> None:
        for obj in self.targetObjects:
            print(obj)

    def testWriteToFile(self) -> None:
        for obj in self.targetObjects:
            filePath = obj.writeToFile()
            with open(filePath, 'r') as f:
                print(f.read())
            print("create a file named " + filePath)
            print("starting remove temp files...", end="")
            try:
                os.remove(filePath)
                print("ok")
            except FileNotFoundError:
                print("failed")


if __name__ == "__main__":
    unittest.main()
