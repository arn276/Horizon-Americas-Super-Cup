# -*- coding: utf-8 -*-
"""
Simulates a season of the Horizon Americas Super Cup (Fictional baseball league).
File uses MLB scoring information to random select winners, scores, and project extra inning games to finish.

@author: aaron
"""

from operator import itemgetter
import sys,datetime, csv, copy, os


from League_Info import leagueFormation
from createMatchups import matchups
from scheduleToDate import schedule
from HistoricSeasonData import historicSeasons
from simulatingResults import simulate
from calculateStandings import standings

## Open Postgres Connection for storing simulations
sys.path.append(r'C:\Users\aaron\Documents')
from connections import connect
conn = connect.postgresConnect()
# Creating a cursor object
cursor = conn.cursor()

## Open dictionary of teams and league format
sys.path.append(r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup')
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
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Schedules'
lst = os.listdir(location)
# Find simulation number
if len(lst) == 0: number = 1
else: number = int(len(lst)/2)+1

##Store Schedule
with open(r''+location+r'\FoundersSchedule_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away'])
    writer.writerows(schedule_conf1)

with open(r''+location+r'\VisionariesSchedule_sim'+str(number)+'.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away'])
    writer.writerows(schedule_conf2)


schedule_conf1_t = copy.deepcopy(schedule_conf1)
schedule_conf1_t = [['Founders']+x for x in schedule_conf1_t]
schedule_conf2_t = copy.deepcopy(schedule_conf2)
schedule_conf2_t = [['Visionaries']+x for x in schedule_conf2_t]

schedule = schedule_conf1_t+schedule_conf2_t
schedule = [ [number]+x for x in schedule]

## Insert into postgres 
fields = '''simulation,conference,gameDate,homeTeam,awayTeam'''
sql = "INSERT into seasons.schedules(xfieldsx) VALUES (%s,%s,%s,%s,%s)"
sql = sql.replace('xfieldsx',fields).replace('''\n        ''','')
for s in schedule:
    cursor.execute(sql, s)
# Commit changes in the database
conn.commit()









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
''' Change commenting to randomly assign winning percents'''
# teamStength = simulate.teamStrength(conferenceTms,rankAvgWinPct)

teamStength = [
    ['Montreal', 0.58,],['Boston', 0.457],['New Haven', 0.253],['New York', 0.531],
    ['Philadelphia', 0.5,],['Pittsburgh', 0.494,],['Toronto', 0.506],['Washington, D.C.', 0.49,],
    ['Winnipeg', 0.547],['St. Paul',  0.571],['Chicago', 0.481],['St. Louis', 0.389],
    ['Detroit',  0.525],['Indianapolis', 0.426],['Akron', 0.562],['Columbus', 0.531],
    
    ['Nashville', 0.509],['Charlotte', 0.508],['Atlanta',  0.466],['Birmingham', 0.491],
    ['Dallas', 0.534],['San Antonio', 0.438],['Monterrey', 0.53],['Merida', 0.51],
    ['Calgary', 0.534],['Vancouver', 0.37],['Denver', 0.623],['Seattle', 0.41],
    ['Oakland', 0.565],['Los Angeles', 0.571],['Phoenix', 0.601],['Tijuana', 0.472]
    ]

#### Simulate Win-Loss
###########################
# 3% for homefield advantage 
results_conf1 = simulate.win_loss( schedule_conf1, teamStength, extrasRate, scoringDic, seasons_exOuts, 3, True)
results_conf2 = simulate.win_loss( schedule_conf2, teamStength, extrasRate, scoringDic, seasons_exOuts, 3, True)



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
def standardizeRowContent(conf,number):
    tempConf = []
    for matchup in conf:
        if len(matchup) == 4: matchup = matchup+['','','','','','']+[number]
        if len(matchup) == 6: matchup = matchup+['','','','']+[number]
        else: matchup = matchup+[number]
        tempConf.append(matchup)
    conf = tempConf
    return conf

results_conf1_final = standardizeRowContent(results_conf1_final,number)
results_conf2_final = standardizeRowContent(results_conf2_final,number)



## Open 
def openExisting(location, file):
    with open(location+file, 'r') as f:
        reader = csv.reader(f)
        existingList = list(reader)
    return existingList


## Open past simulation results
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Results'

conf1_history = openExisting(location, r'\FoundersResultes.csv')
conf2_history = openExisting(location, r'\VisionariesResultes.csv')

conf1_history = conf1_history[1:] + results_conf1_final
conf2_history = conf2_history[1:] + results_conf2_final


## Store simulation Results
with open(r''+location +r'\FoundersResultes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score',
                     'Wrap-up Result','WU Home Score','WU Away Score','WU innings',
                     'Sim Number'])
    writer.writerows(conf1_history)

with open(r''+location +r'\VisionariesResultes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date','Home','Away','Result','Home Score','Away Score',
                     'Wrap-up Result','WU Home Score','WU Away Score','WU innings',
                     'Sim Number'])
    writer.writerows(conf2_history)


results_conf1_final_t = copy.deepcopy(results_conf1_final)
results_conf1_final_t = [['Founders']+x for x in results_conf1_final_t]
results_conf2_final_t = copy.deepcopy(results_conf2_final)
results_conf2_final_t = [['Visionaries']+x for x in results_conf2_final_t]

results = results_conf1_final_t+results_conf2_final_t


## Replace int strings with None
results2 = []
for r in results:
    temp = r[:5]
    if type(r[5]) == str: temp.append(None) 
    else: temp.append(int(r[5]))
    if type(r[6]) == str: temp.append(None) 
    else: temp.append(int(r[6]))
    temp.append(r[7])
    if type(r[8]) == str: temp.append(None) 
    else: temp.append(int(r[8]))
    if type(r[9]) == str: temp.append(None) 
    else: temp.append(int(r[9]))
    if type(r[10]) == str: temp.append(None) 
    else: temp.append(int(r[10]))
    temp.append(r[11])
    results2.append(temp)

## Insert into postgres 
fields = '''conference,gamedate,homeTeam,awayTeam,regulationResult,
            homeScore_reg,awayScore_reg,wrapupResult,homeScore_wu,awayScore_wu,
            outs_wu,simNumber'''
sql = "INSERT into seasons.results(xfieldsx) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sql = sql.replace('xfieldsx',fields).replace('''\n        ''','')
for r in results2:
    cursor.execute(sql, r[:12])
# Commit changes in the database
conn.commit()











###########################    
#### Wind-up Standings             
results_conf = copy.deepcopy(results_conf1+results_conf2)
results_conf_final = copy.deepcopy(results_conf1_final+results_conf2_final)
WU_Results = copy.deepcopy(WU_Results_c1+WU_Results_c2)
## Create pre- and post- Wind-up standings
WUpre_Standings,WUpost_Standings = standings.createStandings(results_conf,WU_Results,results_conf_final,dates,groupTms)


## Create standings list
standingParts = standings.standingLists(WUpre_Standings,WUpost_Standings,leagueFormat)


## Adding sim number, date, rank, and team strength to  standings
standings_final = standings.rankStandings(number,standingParts,teamStength, dates)



## Store simulation standings
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Standings'
standing_history = openExisting(location, r'\seasonStandings.csv')

standing_history = standing_history[1:] + standings_final


with open(r''+location +r'\seasonStandings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Sim Number','Standings Date','Timing','Season Part','Conference','Division','Group',
                     'Rank','Team','Wins','Losses','Ties to Finish','Winning Percent','Team Strength'])
    writer.writerows(standing_history)
    
    
## Insert into playlogs.plays
fields = '''simNumber,standingsDate,timing,seasonPart,conference,division,teamGroup,
            standingRank,team,wins,losses,tiesToFinish,winningPct,teamStrength'''
sql = "INSERT into seasons.standings(xfieldsx) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sql = sql.replace('xfieldsx',fields).replace('''\n        ''','')
for s in standings_final:
    cursor.execute(sql, s)
# Commit changes in the database
conn.commit()  
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    

#############################
#### Other standing Format
# Ordering groups by rank, pre and post
simTeamLst = [ [r[0]]+r[4:7]+[r[8]] for r in standings_final if r[2] == 'pre Wind-up' and r[3] == 'Part 1']
pre1 = [ r[7:9] for r in standings_final if r[2] == 'pre Wind-up' and r[3] == 'Part 1']
post1 = [ r[7:9] for r in standings_final if r[2] == 'post Wind-up' and r[3] == 'Part 1']
pre2 = [ r[7:9] for r in standings_final if r[2] == 'pre Wind-up' and r[3] == 'Part 2']
post2 = [ r[7:9] for r in standings_final if r[2] == 'post Wind-up' and r[3] == 'Part 2']
pre3 = [ r[7:9] for r in standings_final if r[2] == 'pre Wind-up' and r[3] == 'Part 3']
post3 = [ r[7:9] for r in standings_final if r[2] == 'post Wind-up' and r[3] == 'Part 3']
pre4 = [ r[7:9] for r in standings_final if r[2] == 'pre Wind-up' and r[3] == 'Part 4']
post4 = [ r[7:9] for r in standings_final if r[2] == 'post Wind-up' and r[3] == 'Part 4']



rank_final = []
for r in simTeamLst:
    # print([x for x in pre1 if x[1] == r[4]])
    rank = r+[x[0] for x in pre1 if x[1] == r[4]]
    rank = rank+[x[0] for x in post1 if x[1] == r[4]]
    rank = rank+[x[0] for x in pre2 if x[1] == r[4]]
    rank = rank+[x[0] for x in post2 if x[1] == r[4]]
    rank = rank+[x[0] for x in pre3 if x[1] == r[4]]
    rank = rank+[x[0] for x in post3 if x[1] == r[4]]
    rank = rank+[x[0] for x in pre4 if x[1] == r[4]]
    rank = rank+[x[0] for x in post4 if x[1] == r[4]]
    rank_final.append(rank)



## Store simulation standings
location = r'C:\Users\aaron\Documents\GitHub\Horizon-Americas-Super-Cup\windup\simulations\Standings'
rankStanding_history = openExisting(location, r'\rankStandings.csv')

rankStanding_history = rankStanding_history[1:] + rank_final


with open(r''+location +r'\rankStandings.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Sim Number','Conference','Division','Group','Team',
                     'pre-WU1 Rank','post-WU1 Rank','pre-WU2 Rank','post-WU2 Rank',
                     'pre-WU3 Rank','post-WU3 Rank','pre-WU4 Rank','post-WU4 Rank'])
    writer.writerows(rankStanding_history)



## Insert into playlogs.plays
fields = '''simNumber,conference,division,teamGroup,team,
            preWU1rank,postWU1rank,preWU2rank,postWU2rank,
            preWU3rank,postWU3rank,preWU4rank,postWU4rank'''
sql = "INSERT into seasons.rankChanges(xfieldsx) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
sql = sql.replace('xfieldsx',fields).replace('''\n        ''','')
for r in rank_final:
    cursor.execute(sql, r)
# Commit changes in the database
conn.commit()


