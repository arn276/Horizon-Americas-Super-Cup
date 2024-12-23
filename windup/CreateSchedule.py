# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

import pandas as pd
import random
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




## Convert League Dictionary to lists
buildConf = []
for conf in leageDict.keys(): 
    confLst = []
    for div in leageDict[conf].keys():
        divLst = []
        for grp in leageDict[conf][div].keys():
            divLst.append(list(leageDict[conf][div][grp].keys()))
        confLst.append(divLst)
    buildConf.append(confLst)


matchups = []
confLst = []
for conf in buildConf:
    # Group pairings
    divLst = []
    for div in conf:
        grpLst = []
        for grp in div:
            teamLst =[]
            for t in grp:
                for o in grp:
                    if t!=o:
                        teamLst.append([t, o])
            grpLst.append(teamLst)
        divLst.append(grpLst)
    confLst.append(divLst)
    # matchups_grpplay.append(grpLst)
    

