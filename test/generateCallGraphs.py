import os
import re
import sys
import unittest
from os.path import dirname, abspath, join

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

ROOT_DIR = dirname(dirname(abspath(__file__)))
SRC_DIR = join(ROOT_DIR, "src")
DATA_DIR = join(ROOT_DIR, "data")
TEST_DIR = join(ROOT_DIR, "test")

sys.path.append(SRC_DIR)
sys.path.append(DATA_DIR)
sys.path.append(TEST_DIR)

from utils.Configuration import Configuration


def testAllInDir():
    """
    Look at the target directory and search & perform all tests in it.
    """
    prefix = "*" * 70 + "\n" + "*" * 20 + " "
    suffix = "\n" + "*" * 70

    print(f"{prefix}now start to draw call graphs{suffix}", file=sys.stderr)

    current_path = os.path.dirname(os.path.abspath(__file__))  
    graphLog = open(os.path.join(current_path, "callgraph.log"), "w")
    sys.stdout = graphLog
    sys.stderr = graphLog

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=graphLog)

    for root, dirs, files in os.walk(current_path):
        for _dir in dirs:
            if '_' in _dir or '-' in _dir or _dir.startswith("defaultXml"):
                continue
            start_path = os.path.join(current_path, _dir)
            dirSuit = loader.discover(start_path, pattern="test*.py", top_level_dir=start_path)
            for fileSuit in dirSuit:  
                for classSuit in fileSuit:  
 
                    match = re.compile(r'(test\w+)\.\w+\s').findall(classSuit.__str__())
                    if match.__len__() == 0:
                        print("Skip one class suit!!!", file=sys.stderr)
                        continue
                    else:
                        fileName = match[0]
                    graphviz = GraphvizOutput()
                    graphviz.output_file = f"{os.path.join(TEST_DIR, _dir, fileName)}.png"

                    with PyCallGraph(output=graphviz):
                        runner.run(classSuit)
    sys.stderr = sys.__stderr__


if __name__ == "__main__":
    Configuration.parseConfiguration()
    testAllInDir()
    print("generate call graphs done.", file=sys.stderr)
