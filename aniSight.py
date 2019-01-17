################################################################################
# Ani.Sight
################################################################################
# @author         Aaron Ma
# @description    Tool that provides anime ratings insight for AniList users
# @date           January 15th, 2019
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

################################################################################
# Define Global Libraries
################################################################################
dbName = 'anilistDb'

################################################################################
# Functions
################################################################################
# Checks AniList server if it's a valid user name and sets it as active user
def checkUser( userName ):
    print('\n[C] Checking if "' + userName + '" exists in AniList...')
    global user
    userExists = False
    # Variables to retrieve from the graph
    variables = {
        'userName': userName
    }
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
        user = responseData['data']['MediaListCollection']['user']['name'];
        userExists = True
        print('[P] "' + user + '" exists in AniList.')
        print('[A] Setting "' + user + '" as active user.')
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
    global user
    global dbName
    existingUserInDb = False

    print('\n[C] Checking if "' + user + '" is in ' + dbName + '.sqlite...')
    if (checkUser(userName) == True and checkDb() == True):
        # Connect to SQLite file and initialize database cursor
        conn = sqlite3.connect(dbName + '.sqlite')
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM User WHERE name = '" + user + "'")
            userCheck = cur.fetchall()
            userCheckStr = userCheck[0][1]
            if (userCheckStr == user):
                print('[P] ' + user + ' exists in ' + dbName + '.sqlite.')
                existingUserInDb = True
        except:
            print('[F] ' + user + ' does not exist in ' + dbName + '.sqlite.')
    return existingUserInDb

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
            title               TEXT UNIQUE
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
            # print('Adding...', user, (animeId, title, score))
            cur.execute('INSERT OR IGNORE INTO Anime (id, title) VALUES (?,?)', (animeId, title))
            cur.execute('INSERT OR IGNORE INTO Score (user_id, anime_id, score) VALUES (?,?,?)', (userNumber, animeId, score))

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

    # Prompt completion
    print('[S] "' + userName + '" has been added to ' + dbName + '.sqlite')

# Creates a UserData object with AniList data as local variables
def createUserDataObj( userName ):
    print('\nTODO: "Makes user object with user data"')

# Function to add normalized scores
def addNormScore():
    print('\nAdding normalized scores for ' + user.name + ' in ' + dbName + '...')
    # Create sqlite file and initialize database cursor
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()
    try:
        cur.execute('ALTER TABLE Score ADD COLUMN norm_score INTEGER;')
    except:
        pass

    cur.execute('SELECT point_format FROM User WHERE id = ' + str(userNumber))
    ptForm = cur.fetchall()
    ptFormStr = ptForm[0][0]
    print('Point format is ' + ptFormStr + '.')

    if (ptFormStr == 'POINT_100'):
        print('Copying points to norm_score...')
        cur.execute('UPDATE Score SET norm_score = score WHERE user_id = ' + str(userNumber))
    elif (ptFormStr == 'POINT_10_DECIMAL'):
        print('Mulitplying points by 10, converting to int, and inserting into norm_score...')
        cur.execute('UPDATE Score SET norm_score = score*10 WHERE user_id = ' + str(userNumber))
    elif (ptFormStr == 'POINT_10'):
        print('Mulitplying points by 10, and inserting into norm_score...')
    elif (ptFormStr == 'POINT_5'):
        print('Mulitplying points by 20, and inserting into norm_score...')
    elif (ptFormStr == 'POINT_3'):
        print('Mulitplying points by 33, and inserting into norm_score...')
    # Push changes
    conn.commit()
    # Close cursor
    cur.close()
    print('norm_score added to ' + dbName + '.sqlite for ' + user.name + '.')

# Function to normalize the data retrieved for analysis
def normData():
    # Check if a database already exists
    mydir = os.getcwd()
    existingJson = False
    existingDb = False
    for file in os.listdir(mydir):
        if (file == 'anilistDb.sqlite'):
            existingDb = True
        if (file == user.name + '.json'):
            existingJson = True
    # If the database already exists, just call appendNormScore function
    if (existingDb == True and existingJson == True):
        print('\n' + dbName + ' and ' + user.name + '.json already exists.')

    # If the database doesn't exist, create it and call appendNormScore function
    else:
        print('\n' + dbName + ' or ' + user.name + '.json does not exist.')
        print('Creating json for ' + user.name + '...')
        getData()

    print('\nDumping json data for ' + user.name +  'to ' + dbName + '.sqlite...')
    dumpData()
    # Call normalization functions here
    addNormScore()



################################################################################
# Menu Actions
################################################################################
# Prompts for a name and checks if it is valid before assigning it a global var
def setUser():
    global user
    user = input('\nPlease enter your username>> ')
    if (checkUser(user) == True):
        print('\n[S] User name set to "' + user + '".')
    else:
        print('\n[E] Could not set user name: "' + user + '".')
        setUser()

# Prompts for a user name and adds it to an SQLite database
def putDataInDb():
    global user
    user = input('\nPlease enter username to put in the database>> ')
    if (checkUser(user) == True):
        retrieveData(user)
    else:
        print('\n[E] Cannot retrieve AniList data for username: "' + user + '".')

# Grabs data from SQLite database and stores it to local variables
def makeUser():
    global user
    user = input('\nPlease enter username to create object for>> ')
    if (checkUserInDb(user) == True):
        createUserDataObj(user)
    else:
        print('\n[E] Returning to main menu...')

# Function to compare primary user with friend
def normData():
    print('TODO')

# Function to compare primary user with friend
def friendComp():
    print('TODO')
    # friendInput = input("\nPlease enter your friend's username>> ")

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
    '0': setUser,
    '1': putDataInDb,
    '2': makeUser,
    '3': normData,
    '4': friendComp,
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
setUser()

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
    print('q.   <<<< Exit >>>>\n')

    command = input('Enter selection>> ')
    callFunc(command)
