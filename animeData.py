import sqlite3

class AnimeData( object ):
    # Properties
    idMal = 0
    title = ""
    meanScore = 0
    scoreDist = dict()

def makeAniObj( idMal ):
    # Initialize blank object
    animeData = AnimeData()

    # Connect to SQLite file and get anime information
    conn = sqlite3.connect('anilistDb.sqlite')
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
