import json
import requests
import re
import sqlite3
import sys
import os

def retrieveData( userId ):
    print('\n[A] Retrieving AniList data for "' + str(userId) + '"...')
    # Variables to retrieve from the graph
    variables = {
        'userId': userId
    }
    # Query message defined as a multi-line string
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
    with open('data.json', 'w') as outfile:
        json.dump(responseData, outfile, indent=1)
    jsonFile = 'data.json'
    strData = open(jsonFile).read()
    jsonData = json.loads(strData)

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

    mydir = os.getcwd()
    fileList = [ f for f in os.listdir(mydir) if f.endswith(".json")]
    for f in fileList:
        os.remove(os.path.join(mydir, f))

for i in range(90, 180):
    retrieveData(i)
