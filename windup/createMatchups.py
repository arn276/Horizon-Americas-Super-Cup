# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 20:46:35 2025

@author: aaron
"""
import random, copy
from League_Info import leagueFormation

class matchups:
    def allPosibleMatchups(conferenceTms,divisionTms,groupTms):
        confMatchups = []
        for conf in conferenceTms:
            matchupLst = [['Groups Opponent'],['Division Opponent'],['Conference Opponent']]
            for homeTm in conf:
                for awayTm in conf:
                    if homeTm != awayTm:
                        matchupLst = matchups.categorizeMatchup(homeTm,awayTm,conferenceTms,divisionTms,groupTms,matchupLst)
            confMatchups.append(matchupLst)
        return confMatchups
    
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
        
        
    def allUniquePairs(leagueFormat):
        ## Group conferences for efficient scheduling
        confPairingOptions = []
        for conf in leagueFormat:
            for oConf in leagueFormat:
                if conf[0] == oConf[0] and conf[1] != oConf[1]:
                    confPairingOptions.append([conf[3],oConf[3]] )
        ## Finding Unique group pairings
        uniqueConfPairingOptions = []
        for p in confPairingOptions:   
            p.sort()
            if p not in uniqueConfPairingOptions: uniqueConfPairingOptions.append(p)
        return uniqueConfPairingOptions
    

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
    
    
    def cycleGroups(confMatchups, matchupType, maxGames, idealMatchupCt):
        ## Copy for processing
        tempconfMatchups = copy.deepcopy(confMatchups)
        
        matchupSet = []
        for conf in tempconfMatchups:
            retry = True
            conf4Repeat = copy.deepcopy(conf)    
            while retry == True:
                confTemp = []
                while len(leagueFormation.flattenLsts(confTemp))<maxGames:
                    availPair = matchups.availableRoundMatchups(conf[matchupType])
                    roundMatchups = []
                    while len(availPair) >0:
                        conf[1], matchup = matchups.selectMatchup(availPair,conf[matchupType])
                        # matchup = random.choice(availPair)
                        roundMatchups.append(list(matchup))
                        availPair = matchups.remainingRoundMatchups(availPair,[matchup[0],matchup[1]])
                    confTemp.append(list(roundMatchups))
                if len(confTemp) == idealMatchupCt: 
                    retry = False
                else:
                    conf = copy.deepcopy(conf4Repeat)
            matchupSet.append(list(confTemp))
        return matchupSet
    
    
    def confRdPairings(rdList,confMatchups,pairingOrder,rd):
    ## separate each conference rd by group matchups
        for conf in confMatchups:
            confMatchups = []
            for p in pairingOrder[rd]:
                matchupTest = leagueFormation.flattenLsts(p)
                # print(matchupTest)
                for matchup in conf[2][1:]:   
                    if matchup[0] in matchupTest and matchup[1] in matchupTest:
                        # print(matchup)
                        confMatchups.append(matchup)
            rdList.append(confMatchups)
        return rdList
    
    def conferenceScheduling(uniqueConfPairingOptions, confMatchups):
        #### Conference Scheduling            
        ## Random selection of order of group pairingsfor conference matchups
        reduceConfPairingOptions = copy.deepcopy(uniqueConfPairingOptions)
        pairingOrder = []
        while len(pairingOrder)<2:
            tempConfPairingOptions = copy.deepcopy(reduceConfPairingOptions)
            confRd = []
            while len(confRd)<4:
                pair = random.choice(tempConfPairingOptions)
                tempConfPairingOptions = matchups.remainingRoundMatchups(tempConfPairingOptions,pair)
                confRd.append(pair)
                reduceConfPairingOptions.remove(pair)
            pairingOrder.append(confRd)

        ConfRd1=[]                
        ConfRd1 = matchups.confRdPairings(ConfRd1,confMatchups,pairingOrder,0)

        ConfRd2=[]                
        ConfRd2 = matchups.confRdPairings(ConfRd2,confMatchups,pairingOrder,1) 

        ## Set two separate conference rounds for scheduling
        confMatchups[0][2] = ['Conference Rd 1']+ConfRd1[0]
        confMatchups[1][2] = ['Conference Rd 1']+ConfRd1[1]  

        confMatchups[0].append(['Conference Rd 2']+ConfRd2[0])
        confMatchups[1].append(['Conference Rd 2']+ConfRd2[1])


        ## schedule conference matchup order
        maxConferenceGames = len(confMatchups[0][2][1:])*confMatchups[0][2][2][3]
        conferenceMatchups = matchups.cycleGroups(confMatchups, 2, maxConferenceGames, 8)
        conferenceMatchups2 = matchups.cycleGroups(confMatchups, 3, maxConferenceGames, 8)
        
        return conferenceMatchups,conferenceMatchups2
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    