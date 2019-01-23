################################################################################
# Ani.Sight
################################################################################
# @author         Aaron Ma
# @description    Tool that provides anime ratings insight for AniList users
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
from retrieveAniList import *
from userData import *
from animeData import *
from compareData import *

################################################################################
# Variables
################################################################################
dbName = 'aniListDb'
purgeGeneratedFiles = False

################################################################################
# Functions
################################################################################
# Function to compare primary user with another user
def friendComp( userObj, compObj ):
    resultObj = makeCompObj(userObj, compObj)
    results = resultObj.compareList
    sortedResults = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
    for k, v in sortedResults:
        animeObj = makeAniObj(k)
        print(animeObj.title)
        print('...' + userObj.name + ': ' + str(userObj.aniList[k]) + ' // ' + compObj.name + ': ' + str(compObj.aniList[k]))
        print('...Difference: ' + str(v))

# Function to compare primary user with their followers
def followComp( userObj ):
    print('TODO')

# Function to compare primary user with global values
def globalComp( userObj ):
    results = userObj.aniList
    sortedResults = [(k, results[k]) for k in sorted(results, key=results.get, reverse=True)]
    for k, v in sortedResults:
        animeObj = makeAniObj(k)
        stdDev = calcStdDev(animeObj)
        if (userObj.aniList[k] - stdDev > animeObj.meanScore or userObj.aniList[k] + stdDev < animeObj.meanScore):
            print('RARE EVENT: ' + animeObj.title)
            print('...' + userObj.name + ': ' + str(userObj.aniList[k]))
            print('...Global Avg: ' + str(animeObj.meanScore) + ' // Std Dev: ' + str(stdDev))

################################################################################
# Menu Actions
################################################################################
# Script that tests all functions
def testScript():
    print('\nVerify user and retrieve data from AniList')
    print('------------------------------------------')
    userIn = "Prismee"
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            print("[PASS] '" + userIn + "' was inserted into '" + dbName + ".sqlite'.")
        except:
            print("[FAIL] Could not put '" + userIn + "' into '" + dbName + ".sqlite'.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")
    userIn = "yellokirby"
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            print("[PASS] '" + userIn + "' was inserted into '" + dbName + ".sqlite'.")
        except:
            print("[FAIL] Could not put '" + userIn + "' into '" + dbName + ".sqlite'.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")
    userIn = "mteaheart"
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            print("[PASS] '" + userIn + "' was inserted into '" + dbName + ".sqlite'.")
        except:
            print("[FAIL] Could not put '" + userIn + "' into '" + dbName + ".sqlite'.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")
    userIn = "tofugenes"
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            print("[PASS] '" + userIn + "' was inserted into '" + dbName + ".sqlite'.")
        except:
            print("[FAIL] Could not put '" + userIn + "' into '" + dbName + ".sqlite'.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")

    print('\nCompare test users to friends')
    print('-----------------------------')
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

    print('\nCompare test users to its followers')
    print('-----------------------------------')
    followComp(user01)
    followComp(user02)
    followComp(user03)
    followComp(user04)

    print('\nCompare test users to global values')
    print('-----------------------------------')
    globalComp(user01)
    globalComp(user02)
    globalComp(user03)
    globalComp(user04)

# Verifies if the user name exists in the AniList server
def verifyUser():
    userIn = input("\nPlease enter your username>> ")
    print("Verifying user name '" + userIn + "'...")
    if (checkUserName(userIn) == True):
        print("[PASS] '" + userIn + "' exists in AniList.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")

# Prompts for a user name and adds it to an SQLite database
def putDataInDb():
    userIn = input('\nPlease enter username to put in the database>> ')
    print("Inserting '" + userIn + "' into '" + dbName + ".sqlite'...")
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            print("[PASS] '" + userIn + "' was inserted into '" + dbName + ".sqlite'.")
        except:
            print("[FAIL] Could not put '" + userIn + "' into '" + dbName + ".sqlite'.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")

# Script that compares user to another user
def compareScript():
    userIn = input('\nPlease enter first username>> ')
    userComp = input('Please enter username to compare to>> ')
    print('Comparing "' + userIn + '" to "' + userComp + '"...')
    if (checkUserName(userIn) == True):
        if (checkUserName(userComp) == True):
            try:
                putData(userIn, dbName)
                putData(userComp, dbName)
                userObj = normUserData(makeUserObj(userIn))
                compareObj = normUserData(makeUserObj(userComp))
                friendComp(userObj, compareObj)
                print("[PASS] '" + userIn + "' object was compared to '" + userComp + "'.")
            except:
                print("[FAIL] '" + userIn + "' object could not be compared to '" + userComp + "'.")
        else:
            print("[FAIL] '" + userComp + "' does not exist in AniList.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")

# Script that compares user to its followed
def followScript():
    userIn = input('\nPlease enter username>> ')
    print('Comparing "' + userIn + '" to its followed users...')
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            userObj = normUserData(makeUserObj(userIn))
            followComp(userObj)
            print("[PASS] '" + userIn + "' object was compared its followers.")
        except:
            print("[FAIL] '" + userIn + "' object could not be compared to its followers.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")

# Script that compares user to global values
def globalScript():
    userIn = input('\nPlease enter username>> ')
    print('Comparing "' + userIn + '" to global values...')
    if (checkUserName(userIn) == True):
        try:
            putData(userIn, dbName)
            userObj = normUserData(makeUserObj(userIn))
            globalComp(userObj)
            print("[PASS] '" + userIn + "' object was compared to global values.")
        except:
            print("[FAIL] '" + userIn + "' object could not be compared to global values.")
    else:
        print("[FAIL] '" + userIn + "' does not exist in AniList.")

# Script that quits the program
def quitScript():
    if (purgeGeneratedFiles == True):
        mydir = os.getcwd()
        fileList = [ f for f in os.listdir(mydir) if f.endswith(".json") or f.endswith(".sqlite")]
        print('\nRemoving generated files from working directory...')
        for f in fileList:
            print('...Removing: ' + f)
            os.remove(os.path.join(mydir, f))
    sys.exit('Exiting now.\n')

################################################################################
# Switch Variables and Function
################################################################################
# Possible cases to invoke function from main menu
switcher = {
    '1': verifyUser,
    '2': putDataInDb,
    '3': compareScript,
    '4': followScript,
    '5': globalScript,
    '0': testScript,
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
print('=======================================================================')
print('Welcome to Ani.Sight!                                      v.2019.01.23')
print('=======================================================================')

while True:
    print('\n-----------------------------------------------------------------')
    print('What would you like to do?')
    print('-----------------------------------------------------------------')
    print('00.  Test script')
    print('01.  Verify username')
    print('02.  Retrieve data from AniList servers to SQLite database')
    print('03.  Compare two users')
    print('04.  Compare to user followed')
    print('05.  Compare to global values')
    print('q.   <<<< Exit >>>>\n')

    command = input('Enter selection>> ')
    callFunc(command)
