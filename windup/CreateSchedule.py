# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

import pandas as pd
import random, itertools, copy
import sys
sys.path.append(r'C:\Users\aaron\OneDrive\Documents\GitHub\North-American-Super-Cup\windup')
from League_Info import leagueFormation

leageDict = leagueFormation.leagueDict()

def selectGrpMatchups(groupTeams,matchups_grpRd):
    ''' '''
    t1 = random.choice(groupTeams)
    matchup1 = random.choice([x for x in matchups_grpRd if t1 in x])
    t2 = matchup1.copy()
    t2.remove(t1)
    # matchups_grpRd = matchups_grpRd.copy()
    matchup2 = random.choice([x for x in matchups_grpRd if t1 not in x and t2[0] not in x])
    return [matchup1,matchup2]

def flattenLsts(lst):
    return list(itertools.chain.from_iterable(lst))


## Convert League Dictionary to lists
conferenceTms,divisionTms, groupTms = [],[],[]
for conf in leageDict.keys(): 
    confLst = []
    for div in leageDict[conf].keys():
        divLst = []
        
        for grp in leageDict[conf][div].keys():
            groupLst = list(leageDict[conf][div][grp].keys())
            groupTms.append(groupLst)
            divLst.append(groupLst)
        divisionTms.append(flattenLsts(divLst))
        confLst.append(flattenLsts(divLst))
    conferenceTms.append(flattenLsts(confLst))
    

def categorizeMatchup(homeTm,awayTm,conferenceTms,divisionTms,groupTms,matchupLst):
    for grp in groupTms:
        if homeTm in grp and awayTm in grp: 
            seriesHostingInMatchup = 3
            matchupLst[0].append([homeTm,awayTm,'Group',seriesHostingInMatchup])
            return matchupLst
    for div in divisionTms:
        if homeTm in div and awayTm in div: 
            seriesHostingInMatchup = 2
            matchupLst[1].append([homeTm,awayTm,'Division',seriesHostingInMatchup])
            return matchupLst
    else: 
        seriesHostingInMatchup = 1
        matchupLst[2].append([homeTm,awayTm,'Conference',seriesHostingInMatchup])
        return matchupLst


## Find all possible matchups - Home and Away
confMatchups = []
for conf in conferenceTms:
    matchupLst = [['Groups Opponent'],['Division Opponent'],['Conference Opponent']]
    for homeTm in conf:
        for awayTm in conf:
            if homeTm != awayTm:
                matchupLst = categorizeMatchup(homeTm,awayTm,conferenceTms,divisionTms,groupTms,matchupLst)
    confMatchups.append(matchupLst)









## Schedule Group Rounds

def availableRoundMatchups(matchups):
    gameLeftLimit = max(list(set([team[3] for team in matchups[1:]])))
    # return list(set([team[0] for team in matchups[1:] if team[3] == gameLeftLimit]))
    return [team for team in matchups[1:] if team[3] == gameLeftLimit and gameLeftLimit>0]

def selectMatchup(availPair,seasonTracker):
    matchup = random.choice(availPair)
    for i in range(len(seasonTracker)):
        if seasonTracker[i] == matchup: seasonTracker[i][3] = seasonTracker[i][3]-1
    return seasonTracker,matchup
    

def remainingRoundMatchups(matchups,dropTeams): 
    return [team for team in matchups if team[0] not in dropTeams and team[1] not in dropTeams]

## Copy for processing
tempconfMatchups = copy.deepcopy(confMatchups)

allmatchups=[]
for conf in tempconfMatchups:
    confTemp = []
    maxGroupGames = len(conf[0][1:])*conf[0][2][3]
    while len(flattenLsts(confTemp))<maxGroupGames:
        availPair = availableRoundMatchups(conf[0])
        roundMatchups = []
        while len(availPair) >0:
            conf[0], matchup = selectMatchup(availPair,conf[0])
            # matchup = random.choice(availPair)
            roundMatchups.append(list(matchup))
            availPair = remainingRoundMatchups(availPair,[matchup[0],matchup[1]])
        confTemp.append(list(roundMatchups))
    allmatchups.append(list(confTemp))


## Division Scheduling
for conf in tempconfMatchups:
    retry = True
    conf4Repeat = copy.deepcopy(conf)
    while retry == True:
        confTemp = []
        maxGroupGames = len(conf[1][1:])*conf[1][2][3]
        while len(flattenLsts(confTemp))<maxGroupGames:
            availPair = availableRoundMatchups(conf[1])
            roundMatchups = []
            while len(availPair) >0:
                conf[1], matchup = selectMatchup(availPair,conf[1])
                # matchup = random.choice(availPair)
                roundMatchups.append(list(matchup))
                availPair = remainingRoundMatchups(availPair,[matchup[0],matchup[1]])
            confTemp.append(list(roundMatchups))
    
        if len(confTemp) == 16: 
            retry = False
        else:
            conf = copy.deepcopy(conf4Repeat)

    allmatchups.append(list(confTemp))

# len(allmatchups[0][0])
allmatchups[4]
len(confTemp)
