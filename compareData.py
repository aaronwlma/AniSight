class CompareData( object ):
    # Properties
    userObj = ""
    compObj = ""
    compareList = dict()

def makeCompObj( userObj, compObj ):
    # Initialize blank object
    compareData = CompareData()

    # Get and store user information
    compareData.name1 = userObj.name
    compareData.name2 = compObj.name
    compareData.compareList = dict()

    # Loop through anime in both lists and calculate the score difference and
    # store in the compareList
    for animeId in userObj.aniList:
        if animeId in compObj.aniList:
            scoreDiff = userObj.aniList[animeId] - compObj.aniList[animeId]
            compareData.compareList[animeId] = scoreDiff

    # Return compareData object
    return compareData
