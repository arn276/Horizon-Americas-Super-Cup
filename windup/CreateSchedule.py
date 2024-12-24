# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

import pandas as pd
import random, itertools
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
    



def categorizeMatchup():
    


## Find all possible matchups - Home and Away
confMatchups = []
for conf in conferenceTms:
    matchupLst = []
    for h in conf:
        for a in conf:
            if h != a:
                
                matchupLst.append([h,a])
    confMatchups.append(matchupLst)

conferenceTms[0]
