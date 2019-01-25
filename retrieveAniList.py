################################################################################
# Retrieve AniList
################################################################################
# @author         Aaron Ma
# @description    Script that retrieves data from AniList API
# @date           January 25th, 2019
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
import datetime

################################################################################
# Variables
################################################################################
dbName = 'aniListDb'
menuOn = True
saveJson = False
removeFilesOnExit = False

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
          User(name: $userName) {
            name
          }
        }
        '''
    url = 'https://graphql.anilist.co'
    response = requests.post(url, json={'query': query, 'variables': variables})
    if (str(response) == '<Response [200]>'):
        responseData = response.json()
        userAni = responseData['data']['User']['name'];
        if (userName == userAni):
            userExists = True
    return userExists

def checkSqliteDb( dbName ):
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
              avatar {
                large
                medium
              }
              options {
                titleLanguage
                profileColor
              }
              mediaListOptions {
                scoreFormat
              }
              favourites {
                anime {
                  nodes {
                    id
                    title {
                      romaji
                      english
                      native
                      userPreferred
                    }
                    coverImage {
                      extraLarge
                      large
                      medium
                      color
                    }
                    genres
                    averageScore
                    popularity
                    favourites
                    stats {
                      scoreDistribution {
                        score
                        amount
                      }
                    }
                    siteUrl
                  }
                }
              }
              stats {
                watchedTime
              }
            }
            lists {
              entries {
                media {
                    id
                    title {
                      romaji
                      english
                      native
                      userPreferred
                    }
                    coverImage {
                      extraLarge
                      large
                      medium
                      color
                    }
                    genres
                    averageScore
                    popularity
                    favourites
                    stats {
                      scoreDistribution {
                        score
                        amount
                      }
                    }
                    siteUrl
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
    if (saveJson == True):
        with open(str(userId) + '.json', 'w') as outfile:
            json.dump(responseData, outfile, indent=1)
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
                  avatar {
                    large
                    medium
                  }
                  options {
                    titleLanguage
                    profileColor
                  }
                  mediaListOptions {
                    scoreFormat
                  }
                  favourites {
                    anime {
                      nodes {
                        id
                        title {
                          romaji
                          english
                          native
                          userPreferred
                        }
                        coverImage {
                          extraLarge
                          large
                          medium
                          color
                        }
                        genres
                        averageScore
                        popularity
                        favourites
                        stats {
                          scoreDistribution {
                            score
                            amount
                          }
                        }
                        siteUrl
                      }
                    }
                  }
                  stats {
                    watchedTime
                  }
                }
                lists {
                  entries {
                    media {
                        id
                        title {
                          romaji
                          english
                          native
                          userPreferred
                        }
                        coverImage {
                          extraLarge
                          large
                          medium
                          color
                        }
                        genres
                        averageScore
                        popularity
                        favourites
                        stats {
                          scoreDistribution {
                            score
                            amount
                          }
                        }
                        siteUrl
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
    if (saveJson == True):
        with open(str(userName) + '.json', 'w') as outfile:
            json.dump(responseData, outfile, indent=1)
    return jsonData

def makeSqliteDb( dbName ):
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS User (
            id                  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            user_name           TEXT,
            anilist_num         INTEGER UNIQUE,
            point_format        TEXT,
            watched_time        INTEGER,
            title_language      TEXT,
            profile_color       TEXT,
            avatar              TEXT
        );

        CREATE TABLE IF NOT EXISTS List (
            anilist_num_user    INTEGER,
            anilist_num_anime   INTEGER,
            preferred_title     TEXT,
            score               DECIMAL,
            completed_date      TEXT,
            favorite            INTEGER,
            PRIMARY KEY         (anilist_num_user, anilist_num_anime)
        );

        CREATE TABLE IF NOT EXISTS Anime (
            id                  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            title_romaji        TEXT,
            title_english       TEXT,
            title_native        TEXT,
            anilist_num         INTEGER UNIQUE,
            cover_image         TEXT,
            site_url            TEXT,
            average_score       DECIMAL,
            popularity          INTEGER,
            favorited           INTEGER,
            score_10            INTEGER,
            score_20            INTEGER,
            score_30            INTEGER,
            score_40            INTEGER,
            score_50            INTEGER,
            score_60            INTEGER,
            score_70            INTEGER,
            score_80            INTEGER,
            score_90            INTEGER,
            score_100           INTEGER,
            genre_id            INTEGER
        );

        CREATE TABLE IF NOT EXISTS AnimeToGenre (
            id                  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            anilist_num_anime   INTEGER REFERENCES Anime(anilist_num_anime),
            genre_id            INTEGER REFERENCES Genre(id)
        );

        CREATE TABLE IF NOT EXISTS Genre (
            id                  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name                TEXT UNIQUE
        );
    ''')

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

def putDataInSqliteDb( jsonData, dbName ):
    # Create sqlite file and initialize database cursor
    jsonLoad = json.loads(jsonData)
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()

    # Grab the user info in the entry and assign it to variables to store
    userName = jsonLoad['data']['MediaListCollection']['user']['name']
    anilistNumUser = jsonLoad['data']['MediaListCollection']['user']['id']
    pointFormat = jsonLoad['data']['MediaListCollection']['user']['mediaListOptions']['scoreFormat']
    watchedTime = jsonLoad['data']['MediaListCollection']['user']['stats']['watchedTime']
    titleLanguage = jsonLoad['data']['MediaListCollection']['user']['options']['titleLanguage']
    profileColor = jsonLoad['data']['MediaListCollection']['user']['options']['profileColor']
    avatar = jsonLoad['data']['MediaListCollection']['user']['avatar']['large']

    # Create User table and insert retrieved data
    cur.execute('INSERT OR IGNORE INTO User (user_name, anilist_num, point_format, watched_time, title_language, profile_color, avatar) VALUES (?,?,?,?,?,?,?)', (userName, anilistNumUser, pointFormat, watchedTime, titleLanguage, profileColor, avatar))

    # For each list data entry of a user, add it to the database
    for data in jsonLoad['data']['MediaListCollection']['lists']:
        for entry in data['entries']:
            # Grab the anime info in the entry and assign it to variables to store
            titleRomaji = entry['media']['title']['romaji']
            titleEnglish = entry['media']['title']['english']
            titleNative = entry['media']['title']['native']
            anilistNumAnime = entry['media']['id']
            coverImage = entry['media']['coverImage']['extraLarge']
            siteUrl = entry['media']['siteUrl']
            averageScore = entry['media']['averageScore']
            popularity = entry['media']['popularity']
            favorited = entry['media']['favourites']
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
            cur.execute('INSERT OR IGNORE INTO Anime (title_romaji, title_english, title_native, anilist_num, cover_image, site_url, average_score, popularity, favorited, score_10, score_20, score_30, score_40, score_50, score_60, score_70, score_80, score_90, score_100) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (titleRomaji, titleEnglish, titleNative, anilistNumAnime, coverImage, siteUrl, averageScore, popularity, favorited, score10, score20, score30, score40, score50, score60, score70, score80, score90, score100))

            for genre in entry['media']['genres']:
                cur.execute('INSERT OR IGNORE INTO Genre (name) VALUES (?)', (genre,))
                cur.execute('INSERT OR IGNORE INTO AnimeToGenre (anilist_num_anime) VALUES (?)', (anilistNumAnime,))

            # Grab the list info in the entry and assign it to variables to store
            preferredTitle = entry['media']['title']['userPreferred']
            score = entry['score']
            completedYear = entry['completedAt']['year']
            completedMonth = entry['completedAt']['month']
            completedDay = entry['completedAt']['day']
            favorite = 0
            try:
                completedDate = datetime.datetime(completedYear, completedMonth, completedDay)
            except:
                completedDate = datetime.datetime(1,1,1)
            cur.execute('INSERT OR IGNORE INTO List (anilist_num_user, anilist_num_anime, preferred_title, score, completed_date, favorite) VALUES (?,?,?,?,?,?)', (anilistNumUser, anilistNumAnime, preferredTitle, score, completedDate, favorite))

    # For each favorites data entry of a user, mark it as a favorite
    for data in jsonLoad['data']['MediaListCollection']['user']['favourites']['anime']['nodes']:
        idFavorite = data['id']
        cur.execute('UPDATE List SET favorite = 1 WHERE anilist_num_user = ? AND anilist_num_anime = ?', (anilistNumUser, idFavorite))
    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

################################################################################
# Exported Functions
################################################################################
def putData( userName, dbName ):
    makeSqliteDb(dbName)
    putDataInSqliteDb(getDataUN(userName), dbName)

################################################################################
# GUI Functions
################################################################################
def makeAllData():
    start = input('\nEnter starting ID number>> ')
    finish = input('Enter finishing ID number>> ')
    makeSqliteDb(dbName)
    for i in range(int(start), int(finish) + 1):
        print("Adding user ID '" + str(i) + "' to '" + dbName + ".sqlite'...                ",
            end="", flush=True)
        putDataInSqliteDb(getDataID(i), dbName)
        print("[DONE]")

def makeUserData():
    userIn = input('\nEnter user name>> ')
    print("Adding user name '" + userIn + "' to '" + dbName + ".sqlite'...    ",
        end="", flush=True)
    if (checkUserName(userIn) == True):
        makeSqliteDb(dbName)
        putDataInSqliteDb(getDataUN(userIn), dbName)
        print("[DONE]")
    else:
        print("[FAIL]")

def testScript():
    print("Making blank '" + dbName + ".sqlite'...                ",
        end="", flush=True)
    makeSqliteDb(dbName)
    print("[DONE]")

def quitScript():
    if (removeFilesOnExit == True):
        mydir = os.getcwd()
        fileList = [ f for f in os.listdir(mydir) if f.endswith(".json") or f.endswith(".sqlite")]
        for f in fileList:
            print('...Removing: ' + f)
            os.remove(os.path.join(mydir, f))
    sys.exit('Exiting now.\n')

################################################################################
# Switch Variables and Function
################################################################################
# Possible cases to invoke function from main menu
switcher = {
    '0': makeAllData,
    '1': makeUserData,
    '2': testScript,
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
    print('Retrieve AniList Data Tool                           v.2019.01.25')
    print('=================================================================')

    while True:
        print('\n-----------------------------------------------------------------')
        print('What would you like to do?')
        print('-----------------------------------------------------------------')
        print('00.  Scrape AniList server and put into SQLite database')
        print('01.  Input user data into SQLite database')
        print('02.  Run testing script')
        print('q.   <<<< Exit >>>>\n')

        command = input('Enter selection>> ')
        callFunc(command)
