################################################################################
# User Data Object
################################################################################
# @author         Aaron Ma
# @description    Class to define user object with associated functions
# @date           January 23rd, 2019
################################################################################

################################################################################
# Import Libraries
################################################################################
import sqlite3

################################################################################
# Variables
################################################################################
dbName = 'aniListDb'

################################################################################
# Object Definition
################################################################################
class UserData( object ):
    name = ""
    idMal = 0
    pointFormat = ""
    aniList = dict()

################################################################################
# Functions
################################################################################
def makeUserObj( name ):
    # Initialize blank object
    userData = UserData()

    # Connect to SQLite file and initialize database cursor
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()

    # Get and store user information
    cur.execute("SELECT * FROM User WHERE name = '" + name + "'")
    userInfo = cur.fetchone()
    userData.idMal = userInfo[0]
    userData.name = userInfo[1]
    userData.pointFormat = userInfo[2]
    userData.aniList = dict()
    # Get and store user AniList information
    cur.execute("SELECT * FROM Score WHERE user_id = '" + str(userData.idMal) + "'")
    userScores = cur.fetchall()
    for entry in userScores:
        userData.aniList[entry[1]] = entry[2]

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

    # Return userData object
    return userData

def normUserData( userObj ):
    if (userObj.pointFormat == 'POINT_10_DECIMAL'):
        for score in userObj.aniList:
            userObj.aniList[score] = int(userObj.aniList[score]*10)
    elif (userObj.pointFormat == 'POINT_10'):
        for score in userObj.aniList:
            userObj.aniList[score] = userObj.aniList[score]*10
    elif (userObj.pointFormat == 'POINT_5'):
        for score in userObj.aniList:
            userObj.aniList[score] = userObj.aniList[score]*20
    elif (userObj.pointFormat == 'POINT_3'):
        for score in userObj.aniList:
            userObj.aniList[score] = userObj.aniList[score]*33

    # Return userData object
    return userObj
