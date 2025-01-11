# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

import pandas as pd
import random, copy
import sys,datetime, csv, statsapi
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
base = 1969
yearLst = []
for i in range(2024-base+1):
    yearLst.append(base+i)

# Collect all standings in statsApi
allStandings = []
leagueIds = [103,104]
for league in leagueIds:
    for year in yearLst:
        standings = []
        try: # Data by season and league, keeping only team lines, split each field
            season = statsapi.standings(leagueId=league,season=str(year))
            standing = [x for x in season.split('\n') if x[:4] not in ['Nati','Amer','Rank'] and x != '']
            splitToElements = [x.split('  ') for x in standing]
    
            # Keep only those fields with data
            teamElements=[]
            for team in splitToElements:
                teamElements.append([year, league]+[t.strip() for t in team[1:] if t not in ['','-']])
            standings.append(teamElements)
        except KeyError:
            standings.append([year, league])    
        allStandings.append(standings)
 
# Get year, league, team, wins, losses in lists
def checkToSplit_Ls(field):
    if len(field)>3: result = field.split(' ')[0]
    else:result = field
    return result

def checkToSplit_Ws(field):
    if len(field)>3: result = field.split(' ')
    else:result = field
    return result

yearLgBreakout=[]  
for year in allStandings:
    teamBrakeout = []  
    for team in year[0]:    
        # Keep year, league, team name
        entry = team[:2]
        try:
            wins = int(team[2][-3:])
            entry += [team[2][:-3].strip()]+[wins]
            losses = checkToSplit_Ls(team[3])
            entry += [losses]
        except ValueError:
            entry += [team[2]]
            wins = checkToSplit_Ws(team[3])
            if type (wins) is list: entry += wins
            else:
                losses = checkToSplit_Ls(team[4])
                entry += [wins]+[losses]
        teamBrakeout.append(entry)    
    yearLgBreakout.append(teamBrakeout)
    
yearLgBreakout[:10]





#             for team in teamElements:
#                 try: #if wins didn't get split from team, do it here
#                     temp = [year,league]+[team[0][:-3]]
#                     wins = int(team[0][-3:])
#                     temp.append(wins)
#                     [temp.append(x) for x in team[1:2]] 
#                     standings.append(temp)
#                 except ValueError:
#                     if len(team[1])>3: # When wins/losses didn't split
#                         standings.append([year,league]+[x for x in team[0:1]]+[x.split(' ') for x in team[1:2] ][0] )
#                     else: # When wins/losses did split
#                         standings.append([year,league]+[x for x in team[0:1]]+[x.split(' ')[0] for x in team[1:3]])
#         except KeyError:
#             standings.append([year, league])
        
#         allStandings.append(standings)

# # Remove years without standings in statsapi
# allStandings = [x for x in allStandings if len(x)>2]
# # remove cases where win had to be resplit from team about (Phillies 76,79,11)
# allStandings = [[i[:4]  for i in x] for x in allStandings]


    
## Adding Win Percent
[[i+[float(i[3])/(float(i[3])+float(i[4]))]  for i in x] for x in allStandings]

[[i[:4]  for i in x] for x in allStandings][:50]

# Investigate why Phillies didnt split the wins
for x in allStandings:
    for i in x:
        try:
            test = float(i[4])
        except ValueError:
            print(i)
            temp = [i[2][:-3]]
            print(temp)
            wins = int(i[2][-3:])
            print(wins)
            temp.append(wins)
            [temp.append(x) for x in i[3:]] 
            print(temp)



allStandings[55:75]






allStandings = leagueFormation.flattenLsts(allStandings)
histStadnignsDf = pd.DataFrame(allStandings)

histStadnignsDf.head()










with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\historicStandings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(allStandings)









[x for x in [i for i  in splitToElements][0] if x not in ['','-']]

[i for i  in splitToElements][0]


[x.split('  ') for x in standing][1]
        

standing[1].split('  ')[1:]


