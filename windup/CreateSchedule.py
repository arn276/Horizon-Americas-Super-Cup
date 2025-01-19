# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 21:23:50 2024

@author: aaron
"""

from operator import itemgetter
import sys,datetime, csv
sys.path.append(r'C:\Users\aaron\OneDrive\Documents\GitHub\North-American-Super-Cup\windup')

from League_Info import leagueFormation
from createMatchups import matchups
from scheduleToDate import schedule
from HistoricSeasonData import historicSeasons
from simulatingResults import simulate
from calculateStandings import standings

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



#### Sumarize Results
#####################
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

###########################    
#### Wind-up Standings             
## Calculate Standings
WUpre_Standings = [ [[],[],[],[],[],[],[],[]],
                    [[],[],[],[],[],[],[],[]],
                    [[],[],[],[],[],[],[],[]],
                    [[],[],[],[],[],[],[],[]],
                  ] 

WUpre_Standings = standings.WU_Standings(results_conf1+results_conf2, groupTms, dates, 3, WUpre_Standings)
WUpre_Standings = [[sorted(group, key=itemgetter(4), reverse=True) for group in x] for x in WUpre_Standings]


## Calculate Matchup Results of Wrap-up                   
WU_Results_c1 = simulate.WU_createResults(results_conf1, dates, teamStength, extrasRate, scoringDic)   
WU_Results_c2 = simulate.WU_createResults(results_conf2, dates, teamStength, extrasRate, scoringDic)            
# Flatten results into single list 
WU_Results_c1 = leagueFormation.flattenLsts(WU_Results_c1)
WU_Results_c2 = leagueFormation.flattenLsts(WU_Results_c2)

# Combine season and wind-up results
results_conf1 = sorted(results_conf1, key=itemgetter(0), reverse=False)
results_conf2 = sorted(results_conf2, key=itemgetter(0), reverse=False)


results_conf1 = simulate.seasonResultsOrder(results_conf1,WU_Results_c1, dates)
results_conf2 = simulate.seasonResultsOrder(results_conf2,WU_Results_c2, dates)

with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersResultes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score'])
    writer.writerows(results_conf1)

with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesResultes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score'])
    writer.writerows(results_conf2)

## Caculate Wrap-up records
WUpost_Standings = [
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      [[],[],[],[],[],[],[],[]],
                      ]    
WUpost_Standings = standings.WU_Standings(WU_Results_c1+WU_Results_c2, groupTms, dates, 6, WUpost_Standings)        

## Combine standings
WUpost_Standings = standings.finalStandingsSummary(WUpre_Standings,WUpost_Standings)
WUpost_Standings = [[sorted(group, key=itemgetter(4), reverse=True) for group in x] for x in WUpost_Standings]

parts = ['Part 1', 'Part 2', 'Part 3', 'Part 4']
standingParts = []
for i in range(len(parts)):
    for g in range(len(WUpost_Standings[i])):
        confNm = [x[0] for x in leagueFormat if WUpre_Standings[i][g][0][0] in x[3]]
        divNm = [x[1] for x in leagueFormat if WUpre_Standings[i][g][0][0] in x[3]]
        groupNm = [x[2] for x in leagueFormat if WUpre_Standings[i][g][0][0] in x[3]]
        standingParts += [['pre Wind-up',parts[i]]+confNm+divNm+groupNm+team for team in WUpre_Standings[i][g] ]
        
        
        confNm = [x[0] for x in leagueFormat if WUpost_Standings[i][g][0][0] in x[3]]
        divNm = [x[1] for x in leagueFormat if WUpost_Standings[i][g][0][0] in x[3]]
        groupNm = [x[2] for x in leagueFormat if WUpost_Standings[i][g][0][0] in x[3]]
        standingParts += [['post Wind-up',parts[i]]+confNm+divNm+groupNm+team for team in WUpost_Standings[i][g] ]



        
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\seasonStandings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timing','Season Part','Conference','Division','Group',
                     'Team','Wins','Losses','Ties to Finish','Winning Percent'])
    writer.writerows(standingParts)










# Open conference results
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersResultes.csv', 'r') as f:
    reader = csv.reader(f)
    results_conf1 = list(reader)

# Open conference results
with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesResultes.csv', 'r') as f:
    reader = csv.reader(f)
    results_conf2 = list(reader)





         









