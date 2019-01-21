import sqlite3

class CompareData(object):
    # Properities
    name1 = ""
    name2 = ""
    compareList = dict()

    # Initialize
    def __init__(self, name1, name2):
        self.name1 = name1
        self.name2 = name2
        self.compareList = dict()
