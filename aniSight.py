################################################################################
# Ani.Sight
################################################################################
# @author         Aaron Ma
# @description    Tool that provides anime ratings insight for AniList users
# @date           January 21st, 2019
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
from userData import *
from animeData import *
from compareData import *

################################################################################
# Functions - DIDN'T PRECHECK
################################################################################
# ------------------------------------------------------------------------------
# CHECK FUNCTIONS
# ------------------------------------------------------------------------------
# Checks AniList server if it's a valid user name and sets userAni to retrieved
def checkUser( userName ):
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
        if (userName == userAni):
            userExists = True
            print('[P] "' + userName + '" exists in AniList servers')
        else:
            print('[F] "' + userName + '" exists in AniList server as "' + userAni + '"')
    return userExists

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
    print('[S] ..."' + userName + '" data has been retrieved and stored as .json.')

    # Prompt creation of the database
    print('[A] ...Appending "' + userName + '" data to aniListDb.sqlite...')

    # Create sqlite file and initialize database cursor
    conn = sqlite3.connect('aniListDb.sqlite')
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
    print('[S] "' + userName + '" has been added to aniListDb.sqlite')

# Checks if SQLite database exists or not
def checkDb():
    existingDb = False
    print('\n[C] Checking if aniListDb.sqlite exists...')
    mydir = os.getcwd()
    for file in os.listdir(mydir):
        if (file == 'aniListDb.sqlite'):
            existingDb = True
    if (existingDb == True):
        print('[P] aniListDb.sqlite exists.')
    else:
        print('[F] aniListDb.sqlite does not exist.')
    return existingDb

# Checks if user is registered in SQLite database
def checkUserInDb( userName ):
    existingUserInDb = False
    print('\n[C] Checking if "' + userName + '" is in aniListDb.sqlite...')
    # Connect to SQLite file and initialize database cursor
    conn = sqlite3.connect('aniListDb.sqlite')
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM User WHERE name = '" + userAni + "'")
        userCheck = cur.fetchall()
        userCheckStr = userCheck[0][1]
        if (userCheckStr == userName):
            print('[P] ' + userName + ' exists in aniListDb.sqlite')
            existingUserInDb = True
    except:
        print('[F] ' + userName + ' does not exist in aniListDb.sqlite.')
    return existingUserInDb

# Checks user scores against global average, prints titles outside one deviation
def globalComp( userObj ):
    print('\n[A] Comparing "' + userObj.name + '" to global scores...')
    results = userObj.aniList
    sortedResults = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
    for k, v in sortedResults:
        animeObj = makeAniObj(k)
        stdDev = calcStdDev(animeObj)
        if (userObj.aniList[k] - stdDev > animeObj.meanScore or userObj.aniList[k] + stdDev < animeObj.meanScore):
            print('RARE EVENT: ' + animeObj.title)
            print('...' + userObj.name + ': ' + str(userObj.aniList[k]))
            print('...Global Avg: ' + str(animeObj.meanScore) + ' // Std Dev: ' + str(stdDev))
    print('[S] "' + userObj.name + '" comparison to global values completed.')

# Function to compare primary user with friend
def friendComp( userObj, compObj ):
    print('\n[A] Comparing "' + userObj.name + '" to "' + compObj.name + '"...')
    resultObj = makeCompObj(userObj, compObj)
    results = resultObj.compareList
    sortedResults = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
    for k, v in sortedResults:
        animeObj = makeAniObj(k)
        print(animeObj.title)
        print('...' + userObj.name + ': ' + str(userObj.aniList[k]) + ' // ' + compObj.name + ': ' + str(compObj.aniList[k]))
        print('...Difference: ' + str(v))
    print('[S] "' + userObj.name + '" comparison to "' + compObj.name + '" completed.')

################################################################################
# Menu Actions
################################################################################
# Verifies if the user name exists in the AniList server
def verifyUser():
    userIn = input('\nPlease enter your username>> ')
    checkUser(userIn)

# Prompts for a user name and adds it to an SQLite database
def putDataInDb():
    userIn = input('\nPlease enter username to put in the database>> ')
    if (checkUser(userIn) == True):
        retrieveData(userIn)
    else:
        print('\n[E] Cannot retrieve AniList data for username: "' + userIn + '".')

# Script that compares user to global values
def globalScript():
    userIn = input('\nPlease enter first username>> ')
    checkUser(userIn)
    retrieveData(userIn)
    userObj = normUserData(makeUserObj(userIn))
    globalComp(userObj)

# Script that compares active user to an input user
def compareScript():
    userIn = input('\nPlease enter first username>> ')
    userComp = input('Please enter username to compare to>> ')
    checkUser(userIn)
    retrieveData(userIn)
    userObj = normUserData(makeUserObj(userIn))
    checkUser(userComp)
    retrieveData(userComp)
    compareObj = normUserData(makeUserObj(userComp))
    friendComp(userObj, compareObj)

# Script that tests all functions
def testScript():
    print('\nVerify user and retrieve data from AniList')
    print('------------------------------------------')
    checkUser("Prismee")
    retrieveData("Prismee")
    checkUser("yellokirby")
    retrieveData("yellokirby")
    checkUser("mteaheart")
    retrieveData("mteaheart")
    checkUser("tofugenes")
    retrieveData("tofugenes")

    print('\nCompare test users')
    print('------------------')
    # Normalize the user data first”
    user01 = normUserData(makeUserObj("Prismee"))
    user02 = normUserData(makeUserObj("yellokirby"))
    user03 = normUserData(makeUserObj("mteaheart"))
    user04 = normUserData(makeUserObj("tofugenes"))
    # Print comparison list between two users
    friendComp(user01, user02)
    friendComp(user01, user03)
    friendComp(user01, user04)
    friendComp(user02, user03)
    friendComp(user02, user04)
    friendComp(user03, user04)

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
    '0': verifyUser,
    '1': putDataInDb,
    '2': globalScript,
    '3': compareScript,
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
print('Welcome to Ani.Sight!                                v.2019.01.21')
print('=================================================================')

# Main menu
# TEST FXN's will not be available to user, they are for testing purposes
while True:
    print('\n-----------------------------------------------------------------')
    print('What would you like to do?')
    print('-----------------------------------------------------------------')
    print('00.  Verify username')
    print('01.  Retrieve data from AniList servers to SQLite database')
    print('02.  Compare to global data')
    print('03.  Compare two users')
    print('x.   Test script')
    print('q.   <<<< Exit >>>>\n')

    command = input('Enter selection>> ')
    callFunc(command)
