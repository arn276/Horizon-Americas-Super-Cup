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
WU_Standing1,WU_Standing2,WU_Standing3,WU_Standing4 = [],[],[],[]
WU_Results1,WU_Results2,WU_Results3,WU_Results4  = [],[],[],[]
WU_Standings = [WU_Standing1,WU_Standing2,WU_Standing3,WU_Standing4  ] 
WU_Results = [WU_Results1,WU_Results2,WU_Results3,WU_Results4 ] 

for i in range(len(dates)):
    if i > 0:
        teamWins = len([x for x in results_conf1 if x[3] == groupTms[0][0] 
                       and x[0]>dates[i-1] and x[0]<dates[i] ])
        teamLosses = len([x for x in results_conf1 if (x[1] == groupTms[0][0] or x[2] == groupTms[0][0]) 
                          and x[3] != groupTms[0][0] and x[3] != 'Tie in regulation' 
                          and x[0]>dates[i-1] and x[0]<dates[i]])
        teamTies = len([x for x in results_conf1 if (x[1] == groupTms[0][0] or x[2] == groupTms[0][0]) 
                          and x[3] == 'Tie in regulation' 
                          and x[0]>dates[i-1] and x[0]<dates[i]])
        winPct = teamWins/(teamWins+teamLosses)
        WU_Standings[i-1].append([groupTms[0][0],teamWins,teamLosses,teamTies,winPct])
        
        schedule_wu = [x for x in results_conf1 if x[3] == 'Tie in regulation' 
                          and x[0]>dates[i-1] and x[0]<dates[i]]
        WU_Results[i-1] = simulate.win_loss(schedule_wu, teamStength, extrasRate, scoringDic)
        


WU_Results














