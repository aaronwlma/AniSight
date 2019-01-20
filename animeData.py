class AnimeData(object):
    # Properities
    name = ""
    idMal = 0
    meanScore = 0
    scoreDist = dict()

    # Initialize
    def __init__(self, name, idMal, meanScore, scoreDist):
        self.name = name
        self.idMal = idMal
        self.pointFormat = meanScore
        self.scoreDist = dict()
