import unittest

from dataModel.ConfItem import ConfItem
from dataModel.Seed import Seed


class testSeed(unittest.TestCase):
    def test__getitem__(self):
        seed = Seed()
        seed.confItemList.append(ConfItem("lisy", "handsome", "yes"))
        print(seed[0])

    def test__setitem__(self):
        seed = Seed()
        seed.confItemList.append(ConfItem("lisy", "handsome", "yes"))
        seed[0] = ConfItem("lijq", "handsome", "yes")
        print(seed)

    def test__contains__(self):
        seed = Seed()
        seed.confItemList.append(ConfItem("lisy", "handsome", "yes"))
        assert seed.__contains__(ConfItem("lisy", "handsome", "yes"))

    def testIndexOutOfBounds(self):
        seed = Seed()
        seed.confItemList.append(ConfItem("lisy", "handsome", "yes"))
        assert seed[1] == ConfItem()

    def testAddConfItem(self):
        seed = Seed()
        seed.addConfItem(ConfItem("lisy", "handsome", "yes"))

if __name__ == '__main__':
    unittest.main()
