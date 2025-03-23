# -*- coding: utf-8 -*-
"""
Simulates a season of the Horizon Americas Super Cup (Fictional baseball league).
File uses MLB scoring information to random select winners, scores, and project extra inning games to finish.

@author: aaron
"""

from operator import itemgetter
import sys,datetime, csv, copy, os
sys.path.append(r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup')

from League_Info import leagueFormation
from createMatchups import matchups
from scheduleToDate import schedule
from HistoricSeasonData import historicSeasons
from simulatingResults import simulate
from calculateStandings import standings

## Open dictionary of teams and league format
leageDict = leagueFormation.leagueDict()

## Convert League Dictionary to lists of teams
leagueFormat,conferenceTms,divisionTms,groupTms = leagueFormation.teamLsts(leageDict)

## Find all possible matchups - Home and Away
confMatchups = matchups.allPosibleMatchups(conferenceTms,divisionTms,groupTms)

###################################
#### Setup Conference Pairings ####
###################################
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

#########################
#### Create Schedule ####
#########################
conf1,conf2 = schedule.createOrderOfGames(AllMatchups)

## Apply matchups accross dates
base = datetime.date(2010, 4, 1)
schedule_conf1 = schedule.setDates(conf1,base)
schedule_conf2 = schedule.setDates(conf2,base)


## Find group series to make 4 games
schedule_conf1 = schedule.groupSeriesToMake4Games(base,schedule_conf1,groupTms)
schedule_conf2 = schedule.groupSeriesToMake4Games(base,schedule_conf2,groupTms)

## Store simulation Schedule
# Find simulation number
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Standings'
number = len(os.listdir(location))+1

location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Schedules'
lst = os.listdir(location)

##Store Schedule
with open(r''+location+r'\FoundersSchedule_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away'])
    writer.writerows(schedule_conf1)

with open(r''+location+r'\VisionariesSchedule_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away'])
    writer.writerows(schedule_conf2)


##############################
####Historic Scores
##############################
extras, extrasRate,resultRate, extrasResultRate,seasons_exOuts = historicSeasons.historicScores()

##############################
####Historic Standings
##############################
# Pull 1969-2024 standings from StatsApi
# Write to drive
# historicSeasons.formatHistoricSeason()

# Open Historic Standings
with open(r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\historicStandings.csv', 'r') as f:
    reader = csv.reader(f)
    historicList = list(reader)

# Summarize score 
rankAvgWinPct, scoringDic = historicSeasons.summarizeStandings(historicList, resultRate, extras, extrasResultRate)


#### "Play" the games
##########################
# Simulate team strength
teamStength = simulate.teamStrength(conferenceTms,rankAvgWinPct)


# # Open conference schedules
# with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\FoundersSchedule.csv', 'r') as f:
#     reader = csv.reader(f)
#     schedule_conf1 = list(reader)

# # Open conference schedules
# with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\VisionariesSchedule.csv', 'r') as f:
#     reader = csv.reader(f)
#     schedule_conf2 = list(reader)


#### Simulate Win-Loss
###########################
# 3% for homefield advantage 
results_conf1 = simulate.win_loss(schedule_conf1[1:], teamStength, extrasRate, scoringDic, seasons_exOuts, 3, True)
results_conf2 = simulate.win_loss(schedule_conf2[1:], teamStength, extrasRate, scoringDic, seasons_exOuts, 3, True)



#### Sumarize Results
#####################
#convert date strings to dates
# results_conf1 = [[datetime.datetime.strptime(date[0], '%Y-%m-%d').date()]+date[1:] for date in results_conf1 ]
# results_conf2 = [[datetime.datetime.strptime(date[0], '%Y-%m-%d').date()]+date[1:] for date in results_conf2 ]

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


## Calculate Matchup Results of Wrap-up                   
WU_Results_c1 = simulate.WU_createResults(results_conf1, dates, teamStength, extrasRate, scoringDic, seasons_exOuts)   
WU_Results_c2 = simulate.WU_createResults(results_conf2, dates, teamStength, extrasRate, scoringDic, seasons_exOuts)     



# Flatten results into single list 
WU_Results_c1 = leagueFormation.flattenLsts(WU_Results_c1)
WU_Results_c2 = leagueFormation.flattenLsts(WU_Results_c2)

# Combine season and wind-up results
results_conf1 = sorted(results_conf1, key=itemgetter(0), reverse=False)
results_conf2 = sorted(results_conf2, key=itemgetter(0), reverse=False)

results_conf1_final = simulate.seasonResultsOrder(results_conf1,WU_Results_c1, dates)
results_conf2_final = simulate.seasonResultsOrder(results_conf2,WU_Results_c2, dates)

## Standardize cells in row
for conf in [results_conf1_final,results_conf2_final]:
    for matchup in conf:
        if len(matchup) == 4: matchup = matchup+['','','','','','']
        if len(matchup) == 6: matchup = matchup+['','','','']
    

## Store simulation Results
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Results'
lst = os.listdir(location)

with open(r''+location +r'\FoundersResultes_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score',
                     'Wrap-up Result','WU Home Score','WU Away Score','WU innings'])
    writer.writerows(results_conf1_final)

with open(r''+location +r'\VisionariesResultes_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score',
                     'Wrap-up Result','WU Home Score','WU Away Score','WU innings'])
    writer.writerows(results_conf2_final)

###########################    
#### Wind-up Standings             
results_conf = copy.deepcopy(results_conf1+results_conf2)
results_conf_final = copy.deepcopy(results_conf1_final+results_conf2_final)
WU_Results = copy.deepcopy(WU_Results_c1+WU_Results_c2)
## Create pre- and post- Wind-up standings
WUpre_Standings,WUpost_Standings = standings.createStandings(results_conf,WU_Results,results_conf_final,dates,groupTms)


## Create standings list
standingParts = standings.standingLists(WUpre_Standings,WUpost_Standings,leagueFormat)


## Adding rank and team strength to  standings
standings_final = standings.rankStandings(standingParts,teamStength)


## Store simulation standings
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Standings'
lst = os.listdir(location)

with open(r''+location +r'\seasonStandings_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timing','Season Part','Conference','Division','Group',
                     'Rank','Team','Wins','Losses','Ties to Finish','Winning Percent','Team Strength'])
    writer.writerows(standings_final)



















