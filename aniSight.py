################################################################################
# AniList.Compare
################################################################################
# @author         Aaron Ma
# @description    Tool that provides anime ratings insight for AniList users
# @date           January 15th, 2019
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
global dbName
dbName = 'anilistDb'

################################################################################
# Functions
################################################################################
# Function to set the primary global user name
def setUser():
    userInput = input('\nPlease enter your username>> ')
    global user
    user = UserData(userInput)

# Removes generated .json and .sqlite files and exits script
def quitScript():
    mydir = os.getcwd()
    fileList = [ f for f in os.listdir(mydir) if f.endswith(".json") or f.endswith(".sqlite")]
    print('\nRemoving generated files from working directory...')
    for f in fileList:
        print('Removing: ' + f)
        os.remove(os.path.join(mydir, f))
    sys.exit('Exiting now...\n')

# Function to query for relevant information from AniListDB
def getData():
    print('\nRetrieving data for ' + user.name + '...')
    # Variables to retrieve from the graph
    variables = {
        'userName': user.name
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
    # Request info from the following url and save as JSON file
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    if (str(response) == '<Response [200]>'):
        responseData = response.json()
        with open(user.name + '.json', 'w') as outfile:
            json.dump(responseData, outfile, indent=1)
            print('Data saved as JSON file to working directory as ' + user.name + '.json')
    else:
        print(user.name + '.json could not be generated, please try again.')

# Function to dump data into an sqlite file
def dumpData():
    global userNumber

    # Check if a database already exists
    print('\nChecking if ' + user.name + '.json already exists...')
    mydir = os.getcwd()
    existingJson = False
    for file in os.listdir(mydir):
        if (file == user.name + '.json'):
            existingJson = True
    # If the database already exists, just call appendNormScore function
    if (existingJson == True):
        print('\n' + user.name + '.json already exists.')

    # If the database doesn't exist, create it and call appendNormScore function
    else:
        print(user.name + '.json does not exist.')
        print('Creating json for ' + user.name + '...')
        getData()


    # Prompt creating DB message
    print('\nCreating ' + dbName + '.sqlite...')

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

    # Prompt creation of database and adding user
    print('Database ' + dbName + '.sqlite has been created in the working directory.')

    # Check if json data is available

    print('\nAdding ' + user.name + '.json to ' + dbName + '.sqlite...')

    # Parse JSON for relevant information
    jsonFile = user.name + '.json'
    strData = open(jsonFile).read()
    jsonData = json.loads(strData)

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
    print(name + '.json has been added to ' + dbName + '.sqlite')

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

# Function to compare primary user with friend
def friendComp():
    friendInput = input("\nPlease enter your friend's username>> ")

    # Create sqlite file and initialize database cursor
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()
    print('\nChecking if ' + user.name + ' is in ' + dbName + '.sqlite...')
    try:
        cur.execute('SELECT id FROM User WHERE name = ' + user.name + ';')
    except:
        print(user.name + ' is not in ' + dbName + '.sqlite.')
        print('\nAdding ' + user.name + ' to ' + dbName + '.sqlite...')
        normData()
        print(user.name + ' was added to ' + dbName + '.sqlite.')
    print('\nChecking if ' + friendInput + ' is in ' + dbName + '.sqlite...')
    try:
        cur.execute('SELECT id FROM User WHERE name = ' + str(friendInput) + ';')
    except:
        print(friendInput + ' is not in ' + dbName + '.sqlite.')
        print('\nAdding ' + friendInput + ' to ' + dbName + '.sqlite...')
        primaryUser = user.name
        user.name = friendInput
        normData()
        user.name = primaryUser
        print(friendInput + ' was added to ' + dbName + '.sqlite.')
    print('\n' + friendInput + ' is in ' + dbName + '.sqlite.')

################################################################################
# Switch Variables and Function
################################################################################
# Possible cases to invoke function from main menu
switcher = {
    '0': setUser,
    '1': getData,
    '2': dumpData,
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
print('===========================')
print('Welcome to AniList.Compare!')
print('===========================')
setUser()

# Main menu
while True:
    print('\n================================================')
    print('Hi ' + user.name + ', what would you like to do?')
    print('================================================')
    print('00.  Switch to another user name')
    print('01.  Get data as JSON from AniList servers')
    print('02.  Dump retrieved data to SQLite database')
    print('03.  Normalize retrieved JSON data for comparison')
    print('04.  Compare with another user')
    print('q.   <<<< Exit >>>>\n')

    command = input('Enter selection>> ')
    callFunc(command)
