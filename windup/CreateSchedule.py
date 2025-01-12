# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

import pandas as pd
import random, copy
import sys,datetime, csv
sys.path.append(r'C:\Users\aaron\OneDrive\Documents\GitHub\North-American-Super-Cup\windup')

from League_Info import leagueFormation
from createMatchups import matchups
from scheduleToDate import schedule
from HistoricSeasonData import historicSeasons

leageDict = leagueFormation.leagueDict()

## Convert League Dictionary to lists
leagueFormat,conferenceTms,divisionTms,groupTms = leagueFormation.teamLsts(leageDict)

## Find all possible matchups - Home and Away
confMatchups = matchups.allPosibleMatchups(conferenceTms,divisionTms,groupTms)

#### Setup Conference Pairings
## Finding Unique group pairings
uniqueConfPairingOptions = matchups.allUniquePairs(leagueFormat)

## Group Scheduling
maxGroupGames = len(confMatchups[0][0][1:])*confMatchups[0][0][2][3]
groupMatchups = matchups.cycleGroups(confMatchups, 0, maxGroupGames, 18)

## Division Scheduling
maxDivisionGames = len(confMatchups[0][1][1:])*confMatchups[0][1][2][3]
divisionMatchups = matchups.cycleGroups(confMatchups, 1, maxDivisionGames, 16)

## Conference Scheduling   
conferenceMatchups,conferenceMatchups2 = matchups.conferenceScheduling(uniqueConfPairingOptions, confMatchups)
         
#### Combine all the matchups to a single list
AllMatchups = groupMatchups+divisionMatchups+conferenceMatchups+conferenceMatchups2

######################
#### Create Schedule
conf1,conf2 = schedule.createOrderOfGames(AllMatchups)

## Add Dates
base = datetime.date(2010, 4, 1)

schedule_conf1 = schedule.setDates(conf1,base)
schedule_conf2 = schedule.setDates(conf2,base)


#### Find series to make 4 games
schedule_conf1 = schedule.groupSeriesToMake4Games(base,schedule_conf1,groupTms)
schedule_conf2 = schedule.groupSeriesToMake4Games(base,schedule_conf2,groupTms)


with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersSchedule.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(schedule_conf1)

with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesSchedule.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(schedule_conf2)



##############################
####Historic Scores
##############################
locationStr = r'C:\Users\Public\retrosheets\gl2020_23'
season24 = historicSeasons.readSeason(locationStr+r'\gl2024.txt')

regulation = season24[(season24['lengthofgame_outs']>=51) | (season24['lengthofgame_outs']<=54) ]
resultRate = regulation[['roadscor','homescore']].value_counts().reset_index()
resultRate['PercentOfTotal'] = resultRate['count']/resultRate['count'].sum()

resultRate.loc[resultRate['homescore'] > resultRate['roadscor'], 'winner'] = 'Home'
resultRate.loc[resultRate['homescore'] < resultRate['roadscor'], 'winner'] = 'Road'



##############################
####Historic Standings
##############################
# Pull 1969-2024 standings from StatsApi
# Write to drive
# historicSeasons.formatHistoricSeason()

# Open Historic Standings
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\historicStandings.csv', 'r') as f:
    reader = csv.reader(f)
    historicList = list(reader)

years = list(set([int(year[0]) for year in historicList[1:]]))
lgIds = list(set([lg[1] for lg in historicList[1:]]))

allStandings = []
for y in years:
    season = [s for s in historicList if s[0]==str(y)]
    for l in lgIds:
        allStandings.append([t for t in season if t[1]==str(l)])


# Mock winning percents 
yearlyWinPct = []
for year in allStandings:
    winpct = [float(team[5]) for team in year]
    avgWinPct = sum(winpct)/len(winpct)
    while len(winpct)<16:
        winpct.append(avgWinPct)
    winpct.sort(reverse=True)
    yearlyWinPct.append([int(year[0][0])]+[int(year[0][1])]+winpct)  

# Find average league rank winning percent
# will use to simulate team strength
rankAvgWinPct = []
for lg in lgIds:
    league = [lg]
    for i in range(16):
        rankWinPct = [x[i+2] for x in yearlyWinPct[-3:] if x[1]==int(lg)]
        avgWinPct = round(sum(rankWinPct)/len(rankWinPct),3)
        league.append(avgWinPct)
    rankAvgWinPct.append(league)


# Simulate team strength
conf = copy.deepcopy(conferenceTms)
teamStength = []
for i in range(len(rankAvgWinPct)):
    for stength in rankAvgWinPct[i][1:]:
        team = random.choice(conf[i])
        conf[i].remove(team)
        teamStength.append([team,stength])






















