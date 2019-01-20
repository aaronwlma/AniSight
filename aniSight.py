################################################################################
# Ani.Sight
################################################################################
# @author         Aaron Ma
# @description    Tool that provides anime ratings insight for AniList users
# @date           January 19th, 2019
#
# General Notes
# For print statements:     C = CHECK / P = PASS / F = FAIL
#                           A = ACTION / S = SUCCESS / E = ERROR
################################################################################

################################################################################
# Import Libraries
################################################################################
import json
import requests
import re
import sqlite3
import sys
import os
from userData import UserData
from animeData import AnimeData
from compareData import CompareData

################################################################################
# Define Global Libraries
################################################################################
dbName = 'anilistDb'
userAni = ''
user = ''

################################################################################
# Functions
################################################################################
# Checks AniList server if it's a valid user name and sets userAni to retrieved
def checkUser( userName ):
    global userAni
    userExists = False

    print('\n[C] Checking if "' + userName + '" exists in AniList...')
    # Variables to retrieve from the graph
    variables = {'userName': userName}
    # Query message defined as a multi-line string
    query = '''
        query ($userName: String) {
          MediaListCollection(userName: $userName, type: ANIME, status: COMPLETED) {
            user {
              name
            }
          }
        }
        '''
    # Request info from the following url and save info to object
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    # Return true
    if (str(response) != '<Response [200]>'):
        print('[F] "' + userName + '" does not exist in AniList.')
    else:
        responseData = response.json()
        userAni = responseData['data']['MediaListCollection']['user']['name'];
        userExists = True
        print('[P] "' + userName + '" exists in AniList as ' + userAni)
    return userExists

# Checks if SQLite database exists or not
def checkDb():
    global dbName
    existingDb = False

    print('\n[C] Checking if ' + dbName + '.sqlite exists...')
    mydir = os.getcwd()
    for file in os.listdir(mydir):
        if (file == dbName + '.sqlite'):
            existingDb = True
    if (existingDb == True):
        print('[P] ' + dbName + '.sqlite exists.')
    else:
        print('[F] ' + dbName + '.sqlite does not exist.')
    return existingDb

# Checks if user is registered in SQLite database
def checkUserInDb( userName ):
    # global user
    global dbName
    global userAni
    existingUserInDb = False

    print('\n[C] Checking if "' + userName + '" is in ' + dbName + '.sqlite...')
    if (checkUser(userName) == True and checkDb() == True):
        # Connect to SQLite file and initialize database cursor
        conn = sqlite3.connect(dbName + '.sqlite')
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM User WHERE name = '" + userAni + "'")
            userCheck = cur.fetchall()
            userCheckStr = userCheck[0][1]
            if (userCheckStr == userAni):
                print('[P] ' + userAni + ' exists in ' + dbName + '.sqlite.')
                existingUserInDb = True
        except:
            print('[F] ' + userName + ' does not exist in ' + dbName + '.sqlite.')
    return existingUserInDb

# Prompts for a name and checks if it is valid before assigning it a global var
def setUser( userName ):
    global userAni
    global user
    print('\n[A] Setting "' + userName + '" as active user...')
    if (checkUser(userName) == True):
        print('\n[S] "' + userAni + '" set as active user.')
        user = userAni
    else:
        print('\n[E] Could not set user name: "' + userName + '".')

# Gets data from AniList server and dumps it into an SQLite database
def retrieveData( userName ):
    print('\n[A] Retrieving AniList data for "' + userName + '"...')
    # Variables to retrieve from the graph
    variables = {
        'userName': userName
    }
    # Query message defined as a multi-line string
    query = '''
        query ($userName: String) {
          MediaListCollection(userName: $userName, type: ANIME, status: COMPLETED) {
            user {
              id
              name
              mediaListOptions {
                scoreFormat
              }
            }
            lists {
              entries {
                media {
                  id
                  title {
                    romaji
                  }
                  meanScore
                  stats {
                    scoreDistribution {
                      score
                      amount
                    }
                  }
                }
                score
                completedAt {
                  year
                  month
                  day
                }
              }
            }
          }
        }
        '''
    # Request info from the following url and save info to object
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    responseData = response.json()
    with open(userName + '.json', 'w') as outfile:
        json.dump(responseData, outfile, indent=1)
        print('[A] ...Data saved as .json as ' + userName + '.json')
    jsonFile = userName + '.json'
    strData = open(jsonFile).read()
    jsonData = json.loads(strData)

    # Prompt successful data retrieval
    print('[S] "' + userName + '" data has been retrieved and stored as .json.')

    # Prompt creation of the database
    print('\n[A] Appending "' + userName + '" data to ' + dbName + '.sqlite...')

    # Create sqlite file and initialize database cursor
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS User (
            id                  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name                TEXT UNIQUE,
            point_format        TEXT
        );

        CREATE TABLE IF NOT EXISTS Anime (
            id                  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            title               TEXT UNIQUE,
            mean_score          INTEGER,
            score_10            INTEGER,
            score_20            INTEGER,
            score_30            INTEGER,
            score_40            INTEGER,
            score_50            INTEGER,
            score_60            INTEGER,
            score_70            INTEGER,
            score_80            INTEGER,
            score_90            INTEGER,
            score_100            INTEGER
        );

        CREATE TABLE IF NOT EXISTS Score (
            user_id         INTEGER,
            anime_id        INTEGER,
            score           DECIMAL,
            PRIMARY KEY     (user_id, anime_id)
        );
    ''')

    # Grab the user info in the entry and assign it to variables to store
    name = jsonData['data']['MediaListCollection']['user']['name'];
    userNumber = jsonData['data']['MediaListCollection']['user']['id'];
    pointFormat = jsonData['data']['MediaListCollection']['user']['mediaListOptions']['scoreFormat'];

    # Create User table and insert retrieved data
    cur.execute('INSERT OR IGNORE INTO User (id, name, point_format) VALUES (?,?,?)', (userNumber, name, pointFormat))

    # For each data entry of a user, add it to the database
    for data in jsonData['data']['MediaListCollection']['lists']:
        for entry in data['entries']:
            animeId = entry['media']['id']
            title = entry['media']['title']['romaji']
            score = entry['score']
            cur.execute('INSERT OR IGNORE INTO Score (user_id, anime_id, score) VALUES (?,?,?)', (userNumber, animeId, score))
            meanScore = entry['media']['meanScore']
            score10 = 0
            score20 = 0
            score30 = 0
            score40 = 0
            score50 = 0
            score60 = 0
            score70 = 0
            score80 = 0
            score90 = 0
            score100 = 0
            for score in entry['media']['stats']['scoreDistribution']:
                if (score['score'] == 10):
                    score10 = score['amount']
                elif (score['score'] == 20):
                    score20 = score['amount']
                elif (score['score'] == 30):
                    score30 = score['amount']
                elif (score['score'] == 40):
                    score40 = score['amount']
                elif (score['score'] == 50):
                    score50 = score['amount']
                elif (score['score'] == 60):
                    score60 = score['amount']
                elif (score['score'] == 70):
                    score70 = score['amount']
                elif (score['score'] == 80):
                    score80 = score['amount']
                elif (score['score'] == 90):
                    score90 = score['amount']
                elif (score['score'] == 100):
                    score100 = score['amount']
            cur.execute('INSERT OR IGNORE INTO Anime (id, title, mean_score, score_10, score_20, score_30, score_40, score_50, score_60, score_70, score_80, score_90, score_100) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (animeId, title, meanScore, score10, score20, score30, score40, score50, score60, score70, score80, score90, score100))

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

    # Prompt completion
    print('[S] "' + userName + '" has been added to ' + dbName + '.sqlite')

# Creates a UserData object with AniList data as local variables
def createUserDataObj( userName ):
    print('\n[A] Creating user object from ' + userName + '...')
    if (checkUserInDb(userName) == True):
        # Connect to SQLite file and initialize database cursor
        conn = sqlite3.connect(dbName + '.sqlite')
        cur = conn.cursor()
        # Get and store user information
        cur.execute("SELECT * FROM User WHERE name = '" + userAni + "'")
        userInfo = cur.fetchall()
        try:
            idMalRet = userInfo[0][0]
            nameRet = userInfo[0][1]
            pointFormatRet = userInfo[0][2]
            userObj = UserData(nameRet, idMalRet, pointFormatRet)
            print('\n[S] User object created with the following parameters:')
            print('(', userObj.name, userObj.idMal, userObj.pointFormat, ')')
        except:
            print('\n[E] User object could not be created.')
        # Get and store user scores
        print('\n[A] Adding user score from ' + userName + '...')
        cur.execute("SELECT * FROM Score WHERE user_id = '" + str(idMalRet) + "'")
        userScores = cur.fetchall()
        for entry in userScores:
            userObj.aniList[entry[1]] = entry[2]
        return userObj
    else:
        print('\n[E] Returning to main menu...')

# Function to normalize the data retrieved for analysis
def normData( userObject ):
    if (userObject.pointFormat == 'POINT_100'):
        print('...' + userObject.name + ' point format is out of 100.')
    elif (userObject.pointFormat == 'POINT_10_DECIMAL'):
        print('...' + userObject.name + ' point format is out of 10 in decimal.')
        print('[A] Mulitplying scores by 10 and casting to integer...')
        for score in userObject.aniList:
            userObject.aniList[score] = int(userObject.aniList[score]*10)
    elif (userObject.pointFormat == 'POINT_10'):
        print('...' + userObject.name + ' point format is out of 10.')
        print('[A] Mulitplying scores by 10...')
        for score in userObject.aniList:
            userObject.aniList[score] = userObject.aniList[score]*10
    elif (userObject.pointFormat == 'POINT_5'):
        print('...' + userObject.name + ' point format is out of 5.')
        print('[A] Mulitplying scores by 20...')
        for score in userObject.aniList:
            userObject.aniList[score] = userObject.aniList[score]*20
    elif ('...' + userObject.pointFormat == 'POINT_3'):
        print(userObject.name + ' point format is smiley faces.')
        print('[A] Mulitplying scores by 33...')
        for score in userObject.aniList:
            userObject.aniList[score] = userObject.aniList[score]*33
    print('[S] Scores in ' + userObject.name + ' normalized.')

# Function to compare primary user with friend
def friendComp( userObject, friendObject ):
    print('\n[A] Comparing ' + userObject.name + ' to ' + friendObject.name + '...')

    compareObject = CompareData(userObject.name, friendObject.name)
    # Connect to SQLite file and initialize database cursor
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()

    for animeId in userObject.aniList:
        if animeId in friendObject.aniList:
            scoreDiff = userObject.aniList[animeId] - friendObject.aniList[animeId]
            cur.execute("SELECT title FROM Anime WHERE id = '" + str(animeId) + "'")
            animeTitle = cur.fetchone()
            compareObject.compareList[animeTitle[0]] = scoreDiff
            # print(animeTitle[0], scoreDiff)
    results = compareObject.compareList
    sortedResults = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
    for k, v in sortedResults:
        print(k, v)



################################################################################
# Menu Actions
################################################################################
def setActiveUser():
    userIn = input('\nPlease enter your username>> ')
    try:
        setUser(userIn)
    except:
        setActiveUser()

# Prompts for a user name and adds it to an SQLite database
def putDataInDb():
    userIn = input('\nPlease enter username to put in the database>> ')
    if (checkUser(userIn) == True):
        retrieveData(userAni)
    else:
        print('\n[E] Cannot retrieve AniList data for username: "' + userIn + '".')

# Grabs data from SQLite database and stores it to local variables
def makeUser():
    userIn = input('\nPlease enter username to create object for>> ')
    createUserDataObj(userIn)

def testScript():
    checkUser("prismee")
    retrieveData("Prismee")
    checkUser("yellokirby")
    retrieveData("yellokirby")
    checkUser("mteaheart")
    retrieveData("mteaheart")
    checkUser("tofugenes")
    retrieveData("tofugenes")
    user01 = createUserDataObj("prismee")
    user02 = createUserDataObj("yellokirby")
    user03 = createUserDataObj("mteaheart")
    user04 = createUserDataObj("tofugenes")
    normData(user01)
    normData(user02)
    normData(user03)
    normData(user04)
    friendComp(user01, user03)

# Removes generated .json and .sqlite files and exits script
def quitScript():
    mydir = os.getcwd()
    fileList = [ f for f in os.listdir(mydir) if f.endswith(".json") or f.endswith(".sqlite")]
    print('\n[A] Removing generated files from working directory...')
    for f in fileList:
        print('[A] ...Removing: ' + f)
        os.remove(os.path.join(mydir, f))
    sys.exit('[S] Exiting now.\n')

################################################################################
# Switch Variables and Function
################################################################################
# Possible cases to invoke function from main menu
switcher = {
    '0': setActiveUser,
    '1': putDataInDb,
    '2': makeUser,
    '3': normData,
    '4': friendComp,
    'x': testScript,
    'q': quitScript,
    }

def callFunc( argument ):
    func = switcher.get(argument, "Nothing")
    if (func == 'Nothing'):
        print('\nInvalid input, please try again.')
    else:
        return func()

################################################################################
# Main Function
################################################################################

# Welcome message and user info prompt
print('=================================================================')
print('Welcome to Ani.Sight!                                v.01.17.2019')
print('=================================================================')
setActiveUser()

# Main menu
while True:
    print('\n-----------------------------------------------------------------')
    print('Active user: ' + user)
    print('What would you like to do?')
    print('-----------------------------------------------------------------')
    print('00.  Set user name')
    print('01.  Put data from AniList servers to SQLite database')
    print('02.  Create user objects from data in SQLite database')
    print('03.  Normalize local data for comparison')
    print('04.  Compare with another user')
    print('x.   Test script')
    print('q.   <<<< Exit >>>>\n')

    command = input('Enter selection>> ')
    callFunc(command)
