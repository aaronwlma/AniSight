################################################################################
# Anime Data Object
################################################################################
# @author         Aaron Ma
# @description    Class to define Anime object with associated functions
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
class AnimeData( object ):
    idMal = 0
    title = ""
    meanScore = 0
    scoreDist = dict()

################################################################################
# Functions
################################################################################
def makeAniObj( idMal ):
    # Initialize blank object
    animeData = AnimeData()

    # Connect to SQLite file and get anime information
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Anime WHERE id = '" + str(idMal) + "'")
    animeInfo = cur.fetchone()

    # Store anime information
    animeData.idMal = idMal
    animeData.title = animeInfo[1]
    animeData.meanScore = animeInfo[2]
    # Store anime AniList score distribution
    animeData.scoreDist = dict()
    animeData.scoreDist['10'] = animeInfo[3]
    animeData.scoreDist['20'] = animeInfo[4]
    animeData.scoreDist['30'] = animeInfo[5]
    animeData.scoreDist['40'] = animeInfo[6]
    animeData.scoreDist['50'] = animeInfo[7]
    animeData.scoreDist['60'] = animeInfo[8]
    animeData.scoreDist['70'] = animeInfo[9]
    animeData.scoreDist['80'] = animeInfo[10]
    animeData.scoreDist['90'] = animeInfo[11]
    animeData.scoreDist['100'] = animeInfo[12]

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

    # Return animeData object
    return animeData

def calcStdDev( aniObj ):
    # Needed Variables
    mu = aniObj.meanScore
    dist = aniObj.scoreDist
    totalNum = 0
    for k in dist:
        totalNum += dist[k]

    # Formula for calculating standard deviation
    stdDev = (((dist['10']*(10-mu)**2 + dist['20']*(20-mu)**2 +
        dist['30']*(30-mu)**2 + dist['40']*(40-mu)**2 + dist['50']*(50-mu)**2 +
        dist['60']*(60-mu)**2 + dist['70']*(70-mu)**2 + dist['80']*(80-mu)**2 +
        dist['90']*(90-mu)**2 + dist['100']*(100-mu)**2) / totalNum)**0.5)

    # Return the standard deviation
    return stdDev
