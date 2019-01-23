################################################################################
# Retrieve AniList
################################################################################
# @author         Aaron Ma
# @description    Script that retrieves data from AniList API
# @date           January 23rd, 2019
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

################################################################################
# Variables
################################################################################
dbName = 'aniListDb'
menuOn = False

################################################################################
# Check Functions
################################################################################
def checkUserName( userName ):
    userExists = False
    variables = {
        'userName': userName
    }
    query = '''
        query ($userName: String) {
          MediaListCollection(userName: $userName, type: ANIME, status: COMPLETED) {
            user {
              name
            }
          }
        }
        '''
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    if (str(response) == '<Response [200]>'):
        responseData = response.json()
        userAni = responseData['data']['MediaListCollection']['user']['name'];
        if (userName == userAni):
            userExists = True
    return userExists

def checkSqlDb( dbName ):
    dbExists = False
    mydir = os.getcwd()
    for file in os.listdir(mydir):
        if (file == dbName + '.sqlite'):
            dbExists = True
    return dbExists

################################################################################
# Retrieval Functions
################################################################################
def getDataID( userId ):
    variables = {
        'userId': userId
    }
    query = '''
        query ($userId: Int) {
          MediaListCollection(userId: $userId, type: ANIME, status: COMPLETED) {
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
    jsonData = json.dumps(responseData)
    return jsonData

def getDataUN( userName ):
    variables = {
        'userName': userName
    }
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
    jsonData = json.dumps(responseData)
    return jsonData

def putDataInSqlDb( jsonData, dbName ):
    # Create sqlite file and initialize database cursor
    # strData = open(jsonFile).read()
    jsonLoad = json.loads(jsonData)
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
    name = jsonLoad['data']['MediaListCollection']['user']['name'];
    userNumber = jsonLoad['data']['MediaListCollection']['user']['id'];
    pointFormat = jsonLoad['data']['MediaListCollection']['user']['mediaListOptions']['scoreFormat'];

    # Create User table and insert retrieved data
    cur.execute('INSERT OR IGNORE INTO User (id, name, point_format) VALUES (?,?,?)', (userNumber, name, pointFormat))

    # For each data entry of a user, add it to the database
    for data in jsonLoad['data']['MediaListCollection']['lists']:
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

################################################################################
# Exported Functions
################################################################################
def putData( userName, dbName ):
    putDataInSqlDb(getDataUN(userName), dbName)

################################################################################
# GUI Functions
################################################################################
def makeUserData():
    userIn = input('\nEnter user name>> ')
    print("Adding user name '" + userIn + "' to '" + dbName + ".sqlite'...    ",
        end="", flush=True)
    putDataInSqlDb(getDataUN(userIn), dbName)
    print("[DONE]")

def makeAllData():
    start = input('\nEnter starting ID number>> ')
    finish = input('Enter finishing ID number>> ')
    for i in range(int(start), int(finish) + 1):
        print("Adding user ID '" + str(i) + "' to '" + dbName + ".sqlite'...                ",
            end="", flush=True)
        putDataInSqlDb(getDataID(i), dbName)
        print("[DONE]")

def quitScript():
    sys.exit('Exiting now.\n')

################################################################################
# Switch Variables and Function
################################################################################
# Possible cases to invoke function from main menu
switcher = {
    '0': makeUserData,
    '1': makeAllData,
    'q': quitScript,
    }

def callFunc( argument ):
    func = switcher.get(argument, "Nothing")
    if (func == 'Nothing'):
        print('\nInvalid input, please try again.')
    else:
        return func()

################################################################################
# Main Menu
################################################################################
if (menuOn == True):
    print('=================================================================')
    print('Retrieve AniList Data Tool                           v.2019.01.23')
    print('=================================================================')

    while True:
        print('\n-----------------------------------------------------------------')
        print('What would you like to do?')
        print('-----------------------------------------------------------------')
        print('00.  Input user data into database')
        print('01.  Scrape AniList server and put into database')
        print('q.   <<<< Exit >>>>\n')

        command = input('Enter selection>> ')
        callFunc(command)
