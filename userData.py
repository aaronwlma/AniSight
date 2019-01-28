################################################################################
# User Data Object
################################################################################
# @author         Aaron Ma
# @description    Class to define user object with associated functions
# @date           January 28th, 2019
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
    userName = ""
    aniListNum = 0
    pointFormat = ""
    watchedTime = 0
    titleLanguage = ""
    profileColor = ""
    avatar = ""
    following = []
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
    cur.execute("SELECT * FROM User WHERE user_name = '" + name + "'")
    userInfo = cur.fetchone()
    userData.userName = userInfo[1]
    userData.aniListNum = userInfo[2]
    userData.pointFormat = userInfo[3]
    userData.watchedTime = userInfo[4]
    userData.titleLanguage = userInfo[5]
    userData.profileColor = userInfo[6]
    userData.avatar = userInfo[7]
    userData.following = []
    userData.aniList = dict()

    # Get and store user followers user IDs
    cur.execute("SELECT * FROM Following WHERE anilist_num_user = '" + str(userData.aniListNum) + "'")
    followerIds = cur.fetchall()
    for id in followerIds:
        userData.following.append(id[2])

    # Get and store user AniList information
    cur.execute("SELECT * FROM List WHERE anilist_num_user = '" + str(userData.aniListNum) + "'")
    userScores = cur.fetchall()
    for entry in userScores:
        userData.aniList[entry[1]] = entry[3]

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

    # Return userData object
    return userData

def makeUserObjWithId( userId ):
    # Initialize blank object
    userData = UserData()

    # Connect to SQLite file and initialize database cursor
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()

    # Get and store user information
    cur.execute("SELECT * FROM User WHERE anilist_num = '" + str(userId) + "'")
    userInfo = cur.fetchone()
    print(userInfo)
    userData.userName = userInfo[1]
    userData.aniListNum = userInfo[2]
    userData.pointFormat = userInfo[3]
    userData.watchedTime = userInfo[4]
    userData.titleLanguage = userInfo[5]
    userData.profileColor = userInfo[6]
    userData.avatar = userInfo[7]
    userData.following = []
    userData.aniList = dict()

    # Get and store user followers user IDs
    cur.execute("SELECT * FROM Following WHERE anilist_num_user = '" + str(userData.aniListNum) + "'")
    followerIds = cur.fetchall()
    for id in followerIds:
        userData.following.append(id[2])

    # Get and store user AniList information
    cur.execute("SELECT * FROM List WHERE anilist_num_user = '" + str(userData.aniListNum) + "'")
    userScores = cur.fetchall()
    for entry in userScores:
        userData.aniList[entry[1]] = entry[3]

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
