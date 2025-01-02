# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 20:46:35 2025

@author: aaron
"""
import itertools

class matchups:
    def flattenLsts(lst):
        return list(itertools.chain.from_iterable(lst))

    def leagueFormatToList(leageDict):
        conferenceTms,divisionTms, groupTms = [],[],[]
        leagueFormat=[]
        for conf in leageDict.keys(): 
            confLst = []
            # confPairings.append([conf])
            for div in leageDict[conf].keys():
                divLst = []
                for grp in leageDict[conf][div].keys():
                    groupLst = list(leageDict[conf][div][grp].keys())
                    groupTms.append(groupLst)
                    divLst.append(groupLst)
                    leagueFormat.append([conf,div,grp,groupLst])
                divisionTms.append(matchups.flattenLsts(divLst))
                confLst.append(matchups.flattenLsts(divLst))
            conferenceTms.append(matchups.flattenLsts(confLst))
        return leagueFormat,conferenceTms,divisionTms,groupTms 