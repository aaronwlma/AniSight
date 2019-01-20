class UserData(object):
    # Properities
    name = ""
    idMal = 0
    pointFormat = ""
    aniList = dict()

    # Initialize
    def __init__(self, name, idMal, pointFormat):
        self.name = name
        self.idMal = idMal
        self.pointFormat = pointFormat
        self.aniList = dict()
