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

matchups = []
for div in leageDict['Founders'].keys():
    for g in leageDict['Founders'][div].keys():
        groupTeams = list(leageDict['Founders'][div][g].keys())
        matchups_grpRd_all = []
        for t in groupTeams:
            for o in groupTeams:
                if t!=o:
                    matchups_grpRd_all.append([t, o])
        matchups += selectGrpMatchups(groupTeams,matchups_grpRd_all)
matchups