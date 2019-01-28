################################################################################
# Comparison Data Object
################################################################################
# @author         Aaron Ma
# @description    Class to define comparison results as an object with
#                 associated functions
# @date           January 28th, 2019
################################################################################

################################################################################
# Object Definition
################################################################################
class CompareData( object ):
    userObj = ""
    compObj = ""
    compareList = dict()

################################################################################
# Functions
################################################################################
def makeCompObj( userObj, compObj ):
    # Initialize blank object
    compareData = CompareData()

    # Get and store user information
    compareData.name1 = userObj.userName
    compareData.name2 = compObj.userName
    compareData.compareList = dict()

    # Loop through anime in both lists and calculate the score difference and
    # store in the compareList
    for animeId in userObj.aniList:
        if animeId in compObj.aniList:
            scoreDiff = userObj.aniList[animeId] - compObj.aniList[animeId]
            compareData.compareList[animeId] = scoreDiff

    # Return compareData object
    return compareData
