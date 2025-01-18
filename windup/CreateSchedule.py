# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""


import sys,datetime, csv
sys.path.append(r'C:\Users\aaron\OneDrive\Documents\GitHub\North-American-Super-Cup\windup')

from League_Info import leagueFormation
from createMatchups import matchups
from scheduleToDate import schedule
from HistoricSeasonData import historicSeasons
from simulatingResults import simulate

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
    writer.writerow(['Date','Home','Away'])
    writer.writerows(schedule_conf1)

with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesSchedule.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away'])
    writer.writerows(schedule_conf2)



##############################
####Historic Scores
##############################
extras, extrasRate,resultRate, extrasResultRate = historicSeasons.historicScores()

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

# Summarize score 
rankAvgWinPct, scoringDic = historicSeasons.summarizeStandings(historicList, resultRate, extras, extrasResultRate)


#### "Play" the games
##########################
# Simulate team strength
teamStength = simulate.teamStrength(conferenceTms,rankAvgWinPct)


# Open conference schedules
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersSchedule.csv', 'r') as f:
    reader = csv.reader(f)
    schedule_conf1 = list(reader)

# Open conference schedules
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesSchedule.csv', 'r') as f:
    reader = csv.reader(f)
    schedule_conf2 = list(reader)


#### Simulate Win-Loss
###########################
# 3% for homefield advantage 
results_conf1 = simulate.win_loss(schedule_conf1[1:], teamStength, extrasRate, scoringDic, 3, True)
results_conf2 = simulate.win_loss(schedule_conf2[1:], teamStength, extrasRate, scoringDic, 3, True)

with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersResultes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score'])
    writer.writerows(results_conf1)

with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesResultes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score'])
    writer.writerows(results_conf2)


#### Sumarize Results
#####################
# Open conference results
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersResultes.csv', 'r') as f:
    reader = csv.reader(f)
    results_conf1 = list(reader)

# Open conference results
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesResultes.csv', 'r') as f:
    reader = csv.reader(f)
    results_conf2 = list(reader)


#convert date strings to dates
results_conf1 = [[datetime.datetime.strptime(date[0], '%Y-%m-%d').date()]+date[1:] for date in results_conf1[1:]]
results_conf2 = [[datetime.datetime.strptime(date[0], '%Y-%m-%d').date()]+date[1:] for date in results_conf2[1:]]

# Find wind-ups
dates_possible = [date[0] for date in results_conf1 if date[1] == '']
# Find firse date of windup
dates,lastDate = [],base
for d in dates_possible:
    difference = abs((d - lastDate).days)
    if difference > 30:
       dates.append(d) 
    lastDate = d
dates = [base]+dates

    
#Wind-up Standings

from operator import itemgetter
def WU_Standings(results_conf, groups, dates, winnerCol, WUpre_Standings):
    for i in range(len(dates)):
        if i > 0:
            for division in range(len(groups)):
                for team in groupTms[division]:
                    teamWins = len([x for x in results_conf if x[winnerCol] == team 
                                   and x[0]>=dates[i-1] and x[0]<dates[i] ])
                    teamLosses = len([x for x in results_conf if (x[1] == team  or x[2] == team ) 
                                      and x[winnerCol] != team and x[winnerCol] != 'Tie in regulation' 
                                      and x[0]>=dates[i-1] and x[0]<dates[i]])
                    teamTies = len([x for x in results_conf if (x[1] == team  or x[2] == team ) 
                                      and x[winnerCol] == 'Tie in regulation' 
                                      and x[0]>=dates[i-1] and x[0]<dates[i]])
                    try:
                        winPct = round(teamWins/(teamWins+teamLosses),3)
                    except ZeroDivisionError:
                        winPct = None
                    WUpre_Standings[i-1][division].append([team ,teamWins,teamLosses,teamTies,winPct])
                # WUpre_Standings[i-1][division] = sorted(WUpre_Standings[i-1][division], key=itemgetter(4), reverse=True)
    return WUpre_Standings
                    
## Calculate Standings
WUpre_Standings = [
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      ] 

WUpre_Standings = WU_Standings(results_conf1+results_conf2, groupTms, dates, 3, WUpre_Standings)
WUpre_Standings[0]

## Calculate Results of Wrap-up
def WU_createResults(results_conf, dates, teamStength, extrasRate, scoringDic):
    WU_Results = []
    for i in range(len(dates)):
        if i > 0:
            schedule_wu = [x for x in results_conf if x[3] == 'Tie in regulation' 
                              and x[0]>=dates[i-1] and x[0]<dates[i]]
            sim = simulate.win_loss(schedule_wu, teamStength, extrasRate, scoringDic)
            WU_Results.append(sim)
    return WU_Results
                      
WU_Results_c1 = WU_createResults(results_conf1, dates, teamStength, extrasRate, scoringDic)   
WU_Results_c2 = WU_createResults(results_conf2, dates, teamStength, extrasRate, scoringDic)            
            
WU_Results_c1 = leagueFormation.flattenLsts(WU_Results_c1)
WU_Results_c2 = leagueFormation.flattenLsts(WU_Results_c2)


## Caculate Wrap-up records
WUpost_Standings = [
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      ]    
WUpost_Standings = WU_Standings(WU_Results_c1+WU_Results_c2, groupTms, dates, 6, WUpost_Standings)        


## Combine standings

for WU in range(len(WUpost_Standings)):
    for group in range(len(WUpost_Standings[WU])):
        for team in range(len(WUpost_Standings[WU][group])):
            t = WUpost_Standings[WU][group][team][0]
            WU_wins = WUpost_Standings[WU][group][team][1]
            WU_wins += [x for x in WUpre_Standings[WU][group] if x[0] == t ][0][1]
            
            WU_losses = WUpost_Standings[WU][group][team][2]
            WU_losses += [x for x in WUpre_Standings[WU][group] if x[0] == t ][0][2]
            
            if WU >0:
                WU_wins += [x for x in WUpost_Standings[WU-1][group] if x[0] == t ][0][1]
                WU_losses += [x for x in WUpost_Standings[WU-1][group] if x[0] == t ][0][2]
            
            WU_winpct = round(WU_wins/(WU_wins+WU_losses),3)
            WUpost_Standings[WU][group][team] = [t,WU_wins, WU_losses, WUpost_Standings[WU][group][team][3], WU_winpct]








            
len(WUpre_Standings[0])
WUpost_Standings[0][0]


[x for x in WU_Results_c1 if x[1] == 'Akron' or x[2] == 'Akron']

[x for x in results_conf1 if (x[1] == 'Akron' or x[2] == 'Akron') and x[3] == 'Tie in regulation']


# WU_Results_c1[0][0]

# WUpre_Standings_c1[0]









