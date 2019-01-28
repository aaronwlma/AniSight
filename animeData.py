################################################################################
# Anime Data Object
################################################################################
# @author         Aaron Ma
# @description    Class to define Anime object with associated functions
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
class AnimeData( object ):
    titleRomaji = ""
    titleEnglish = ""
    titleNative = ""
    aniListNum = 0
    coverImage = ""
    siteUrl = ""
    averageScore = 0
    popularity = 0
    favorited = 0
    scoreDist = dict()

################################################################################
# Functions
################################################################################
def makeAniObj( aniId ):
    # Initialize blank object
    animeData = AnimeData()

    # Connect to SQLite file and get anime information
    conn = sqlite3.connect(dbName + '.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Anime WHERE anilist_num = '" + str(aniId) + "'")
    animeInfo = cur.fetchone()

    # Store anime information
    animeData.titleRomaji = animeInfo[1]
    animeData.titleEnglish = animeInfo[2]
    animeData.titleNative = animeInfo[3]
    animeData.aniListNum = aniId
    animeData.coverImage = animeInfo[5]
    animeData.siteUrl = animeInfo[6]
    animeData.averageScore = animeInfo[7]
    animeData.popularity = animeInfo[8]
    animeData.favorited = animeInfo[9]
    # Store anime AniList score distribution
    animeData.scoreDist = dict()
    animeData.scoreDist['10'] = animeInfo[10]
    animeData.scoreDist['20'] = animeInfo[11]
    animeData.scoreDist['30'] = animeInfo[12]
    animeData.scoreDist['40'] = animeInfo[13]
    animeData.scoreDist['50'] = animeInfo[14]
    animeData.scoreDist['60'] = animeInfo[15]
    animeData.scoreDist['70'] = animeInfo[16]
    animeData.scoreDist['80'] = animeInfo[17]
    animeData.scoreDist['90'] = animeInfo[18]
    animeData.scoreDist['100'] = animeInfo[19]

    # Push changes
    conn.commit()
    # Close cursor
    cur.close()

    # Return animeData object
    return animeData

def calcStdDev( aniObj ):
    # Needed Variables
    mu = aniObj.averageScore
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
