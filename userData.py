import sqlite3

class UserData( object ):
    # Properties
    name = ""
    idMal = 0
    pointFormat = ""
    aniList = dict()

def makeUserObj( name ):
    # Initialize blank object
    userData = UserData()

    # Connect to SQLite file and initialize database cursor
    conn = sqlite3.connect('anilistDb.sqlite')
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
