import unittest

from dataModel.ConfItem import ConfItem


class testConfItem(unittest.TestCase):
    def testCreator(self):
        confItem = ConfItem("lisy", "handsome", "yes")
        print(confItem)

    def testProperty(self):
        confItem = ConfItem()
        confItem.name = "lisy"
        print(confItem.name)
        confItem.type = "handsome"
        print(confItem.type)
        confItem.value = "yes"
        print(confItem.value)

    def test__str__(self):
        confItem = ConfItem("lisy", "handsome", "yes")
        print(confItem.__str__())

    def test__eq__(self):
        confItem = ConfItem("lisy", "handsome", "yes")
        confItem2 = ConfItem("lijq", "handsome", "yes")
        print(confItem == confItem2)
        print(confItem == 3)



if __name__ == '__main__':
    unittest.main()
