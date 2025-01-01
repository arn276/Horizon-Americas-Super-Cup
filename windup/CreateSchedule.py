# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

import pandas as pd
import random, itertools, copy
import sys,datetime, csv
sys.path.append(r'C:\Users\aaron\OneDrive\Documents\GitHub\North-American-Super-Cup\windup')
from League_Info import leagueFormation

leageDict = leagueFormation.leagueDict()

# def selectGrpMatchups(groupTeams,matchups_grpRd):
#     ''' '''
#     t1 = random.choice(groupTeams)
#     matchup1 = random.choice([x for x in matchups_grpRd if t1 in x])
#     t2 = matchup1.copy()
#     t2.remove(t1)
#     # matchups_grpRd = matchups_grpRd.copy()
#     matchup2 = random.choice([x for x in matchups_grpRd if t1 not in x and t2[0] not in x])
#     return [matchup1,matchup2]

def flattenLsts(lst):
    return list(itertools.chain.from_iterable(lst))


## Convert League Dictionary to lists
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



##############
#### Find all possible matchups - Home and Away
##############
confMatchups = []
for conf in conferenceTms:
    matchupLst = [['Groups Opponent'],['Division Opponent'],['Conference Opponent']]
    for homeTm in conf:
        for awayTm in conf:
            if homeTm != awayTm:
                matchupLst = categorizeMatchup(homeTm,awayTm,conferenceTms,divisionTms,groupTms,matchupLst)
    confMatchups.append(matchupLst)


#### Setup Conference Pairings
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
            while len(flattenLsts(confTemp))<maxGames:
                availPair = availableRoundMatchups(conf[matchupType])
                roundMatchups = []
                while len(availPair) >0:
                    conf[1], matchup = selectMatchup(availPair,conf[matchupType])
                    # matchup = random.choice(availPair)
                    roundMatchups.append(list(matchup))
                    availPair = remainingRoundMatchups(availPair,[matchup[0],matchup[1]])
                confTemp.append(list(roundMatchups))
            if len(confTemp) == idealMatchupCt: 
                retry = False
            else:
                conf = copy.deepcopy(conf4Repeat)
        matchupSet.append(list(confTemp))
    return matchupSet


#### Group Scheduling
maxGroupGames = len(confMatchups[0][0][1:])*confMatchups[0][0][2][3]
groupMatchups = cycleGroups(confMatchups, 0, maxGroupGames, 18)

#### Division Scheduling
maxDivisionGames = len(confMatchups[0][1][1:])*confMatchups[0][1][2][3]
divisionMatchups = cycleGroups(confMatchups, 1, maxDivisionGames, 16)



#### Conference Scheduling            
## Random selection of order of group pairingsfor conference matchups
reduceConfPairingOptions = copy.deepcopy(uniqueConfPairingOptions)
pairingOrder = []
while len(pairingOrder)<2:
    tempConfPairingOptions = copy.deepcopy(reduceConfPairingOptions)
    confRd = []
    while len(confRd)<4:
        pair = random.choice(tempConfPairingOptions)
        tempConfPairingOptions = remainingRoundMatchups(tempConfPairingOptions,pair)
        confRd.append(pair)
        reduceConfPairingOptions.remove(pair)
    pairingOrder.append(confRd)


## separate each conference rd by group matchups
def confRdPairings(rdList,confMatchups,pairingOrder,rd):
    for conf in confMatchups:
        confMatchups = []
        for p in pairingOrder[rd]:
            matchupTest = flattenLsts(p)
            # print(matchupTest)
            for matchup in conf[2][1:]:   
                if matchup[0] in matchupTest and matchup[1] in matchupTest:
                    # print(matchup)
                    confMatchups.append(matchup)
        rdList.append(confMatchups)
    return rdList

ConfRd1=[]                
ConfRd1 = confRdPairings(ConfRd1,confMatchups,pairingOrder,0)

ConfRd2=[]                
ConfRd2 = confRdPairings(ConfRd2,confMatchups,pairingOrder,1) 

## Set two separate conference rounds for scheduling
confMatchups[0][2] = ['Conference Rd 1']+ConfRd1[0]
confMatchups[1][2] = ['Conference Rd 1']+ConfRd1[1]  

confMatchups[0].append(['Conference Rd 2']+ConfRd2[0])
confMatchups[1].append(['Conference Rd 2']+ConfRd2[1])


## schedule conference matchup order
maxConferenceGames = len(confMatchups[0][2][1:])*confMatchups[0][2][2][3]
conferenceMatchups = cycleGroups(confMatchups, 2, maxConferenceGames, 8)
conferenceMatchups2 = cycleGroups(confMatchups, 3, maxConferenceGames, 8)


#### Combine all the matchups to a single list
AllMatchups = groupMatchups+divisionMatchups+conferenceMatchups+conferenceMatchups2



######################
#### Create Schedule

seriesOrder = [
                ['g','g','g','g','g','g','c1','c1','c1','c1'],
               ['d','d','d','d','d','d','d','d','d','d','d','d','d','d','d','d'],
               ['g','g','g','g','c2','c2','c2','c2','c2','c2','c2','c2'],
               ['g','g','g','g','c1','c1','c1','c1','g','g','g','g']
               ]

matchupsForScheduling = copy.deepcopy(AllMatchups)

def scheduleGames(seriesOrder,matchupsForScheduling,group,division,conf1,conf2):
    confSchedule=[]
    for q in range(len(seriesOrder)):
        for s in seriesOrder[q]:
            days = [[],[],[]]
            if s == 'g': pair = group
            if s == 'd': pair = division
            if s == 'c1': pair = conf1
            if s == 'c2': pair = conf2
            roundMatchups = copy.deepcopy(matchupsForScheduling[pair][0]) ## This round matchups
            matchupsForScheduling[pair].remove(roundMatchups) ## Remove from list
            for game in roundMatchups:
                gameNo = 3
                while gameNo>0:
                    gameNo -= 1
                    days[gameNo].append([game[0],game[1]])
            confSchedule.append(days) 
        if q == 1: confSchedule.append([[],[],[],[]])
        else: confSchedule.append([[],[],[]])
    return confSchedule
       
conf1 = scheduleGames(seriesOrder,matchupsForScheduling,0,2,4,6)
conf2 = scheduleGames(seriesOrder,matchupsForScheduling,1,3,5,7)

#### Add Dates
base = datetime.date(2010, 4, 1)
date_list = [base + datetime.timedelta(days=x) for x in range(225)] ##185

schedules = []
for series in range(len(conf1)):
    for leagueGame in range(len(conf1[series])):
        if len(conf1[series][leagueGame]) == 0:
            if len([date[1] for date in schedules if date[0] == date_list[0]])>1 : del date_list[0]
            schedules.append([date_list[0]]+['',''])
            del date_list[0]
        else:
            for game in range(len(conf1[series][leagueGame])):
                prevDayTeams = [date[1] for date in schedules if date[0] == date_list[0]]+[date[2] for date in schedules if date[0] == date_list[0]]
                homechk = conf1[series][leagueGame][game][0] in prevDayTeams
                awaychk = conf1[series][leagueGame][game][1] in prevDayTeams
                if game <5 and homechk == False and awaychk == False:
                    schedules.append([date_list[0]]+conf1[series][leagueGame][game])
                else: schedules.append([date_list[1]]+conf1[series][leagueGame][game])
            del date_list[0]
    if series != len(conf1)-1:
        if len(conf1[series+1][0]) != 0 and len(conf1[series-1][0]) and len(conf1[series][0])!= 0 and series%3==0:
            del date_list[0]


#### Find series to make 4 games
## season game date list
date_list = [base + datetime.timedelta(days=x) for x in range(186)]
excludionLst = [d[0] for d in schedules if d[1] == '']
maxDt = max([d[0] for d in schedules if d[1] != ''])
date_list = [d for d in date_list if d not in excludionLst and d < maxDt]

def findBackToBackOff(schedules,team,date_list):
    backToBackOpen = []
    # Days home plays
    hmTeamDates = [date[0] for date in schedules if date[1] == team or date[2] == team]
    # Days home doesn't play
    hmTeamDates = [d for d in date_list if d not in  hmTeamDates]
    for date in range(len(hmTeamDates)):
        if date != 0:
            if abs((hmTeamDates[date] - hmTeamDates[date-1]).days) == 1:
                backToBackOpen.append(hmTeamDates[date])
                backToBackOpen.append(hmTeamDates[date-1])
    return backToBackOpen



for group in groupTms[2:3]:
    #List all group games by group
    groupGames = [game for game in schedules if game[1] in group and game[2] in group]
    #Find unique
    uniqueLst = []
    for matchup in [[game[1],game[2]] for game in groupGames]:
        if matchup not in uniqueLst: uniqueLst.append(matchup)
    #Find dates team could extend series
    FourthGmOption = []
    for matchup in uniqueLst:
        ## date where both teams have back to back days off
        homeTmPairOff = findBackToBackOff(schedules,matchup[0],date_list)
        awayTmPairOff = findBackToBackOff(schedules,matchup[1],date_list)
        pairedOffPriority = [date for date in homeTmPairOff if date in awayTmPairOff]
        # print(matchup)
        checkDates = [date[0] for date in schedules if date[1] == matchup[0] and date[2] == matchup[1]]
        for date in checkDates:
            if date != base:
                prevDt = date+datetime.timedelta(days=-1)
                prevDayTeams = [match[1] for match in schedules if match[0] == prevDt]+[match[2] for match in schedules if match[0] == prevDt]
                homechk = matchup[0] in prevDayTeams
                awaychk = matchup[1] in prevDayTeams
            if homechk == False and awaychk == False:
                FourthGmOption.append(prevDt)
                # print('pre')
                # print(prevDt)
            else:
                tomorrow = date+datetime.timedelta(days=1) 
                tomorrowTeams = [match[1] for match in schedules if match[0] == tomorrow]+[match[2] for match in schedules if match[0] == tomorrow]
                homechk = matchup[0] in tomorrowTeams
                awaychk = matchup[1] in tomorrowTeams
                if homechk == False and awaychk == False:
                    FourthGmOption.append(tomorrow)
                    # print('tom')
                    # print(tomorrow)
        
        try:
            priorityDate = max([date for date in FourthGmOption if date in pairedOffPriority])
            schedules.append([priorityDate]+matchup)
            print(matchup)
            print('priority')
            print(priorityDate)
        except ValueError:
            FourthGmOption = [date for date in FourthGmOption if date not in excludionLst]
            try: 
                schedules.append([max(FourthGmOption)]+matchup)
                print(matchup)
                print('4thOption')
                print(max(FourthGmOption))
            except ValueError:
                minDt, maxDt = datetime.date(2010, 5, 1),datetime.date(2010, 9, 1)
                doubleHeader = random.choice([game for game in groupGames if game[0]> minDt and game[0]<maxDt ])
                print(matchup)
                print('double')
                print(doubleHeader)
                schedules.append(doubleHeader)
                
                
                
                
                
schedules[-10:]





with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\schedule.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(schedules)
















# backToBackOpen = []
# # Days home plays
# hmTeamDates = [date[0] for date in schedules if date[1] == uniqueLst[0][0] or date[2] == uniqueLst[0][0]]
# # Days home doesn't play
# hmTeamDates = [d for d in date_list if d not in  hmTeamDates]
# for date in range(len(hmTeamDates)):
#     if date != 0:
#         if abs((hmTeamDates[date] - hmTeamDates[date-1]).days) == 1:
#             backToBackOpen.append(hmTeamDates[date])
#             backToBackOpen.append(hmTeamDates[date-1])

# backToBackOpen2 = []
# # Days home plays
# hmTeamDates = [date[0] for date in schedules if date[1] == uniqueLst[0][1] or date[2] == uniqueLst[0][1]]
# # Days home doesn't play
# hmTeamDates = [d for d in date_list if d not in  hmTeamDates]
# for date in range(len(hmTeamDates)):
#     if date != 0:
#         if abs((hmTeamDates[date] - hmTeamDates[date-1]).days) == 1:
#             backToBackOpen2.append(hmTeamDates[date])
#             backToBackOpen2.append(hmTeamDates[date-1])


# [date for date in backToBackOpen if date in backToBackOpen2]



