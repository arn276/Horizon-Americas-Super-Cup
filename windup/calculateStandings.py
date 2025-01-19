# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 19:56:12 2025

@author: aaron
"""
import csv
from operator import itemgetter

class standings():
    def upToPoint_standings(results_conf_final, dates, winnerCol, i, team):
        teamWins_post = len([x for x in results_conf_final if x[winnerCol] == team 
                       # and x[0]>=dates[i-1] 
                       and x[0]<=dates[i] ])
        teamLosses_post = len([x for x in results_conf_final if (x[1] == team  or x[2] == team ) 
                          and x[winnerCol] != team and x[winnerCol] != 'Tie in regulation' 
                          # and x[0]>=dates[i-1] 
                          and x[0]<=dates[i]])
        return teamWins_post,teamLosses_post
    
    
    def period_standings(results_conf_final, dates, winnerCol, i, team):
        teamWins_post = len([x for x in results_conf_final if x[winnerCol] == team 
                       and x[0]>=dates[i-1] 
                       and x[0]<=dates[i] ])
        teamLosses_post = len([x for x in results_conf_final if (x[1] == team  or x[2] == team ) 
                          and x[winnerCol] != team and x[winnerCol] != 'Tie in regulation' 
                          and x[0]>=dates[i-1] 
                          and x[0]<=dates[i]])
        teamTies_post = len([x for x in results_conf_final if (x[1] == team  or x[2] == team ) 
                          and x[winnerCol] == 'Tie in regulation' 
                          and x[0]>=dates[i-1] 
                          and x[0]<=dates[i]])
        return teamWins_post,teamLosses_post,teamTies_post
    
    
    def createStandings(results_conf,WU_Results,results_conf_final,dates,groupTms):
        ## Calculate Standings
        WUpre_Standings = [ [[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[]],
                            [[],[],[],[],[],[],[],[]],
                          ] 

        WUpost_Standings = [
                              [[],[],[],[],[],[],[],[]],
                              [[],[],[],[],[],[],[],[]],
                              [[],[],[],[],[],[],[],[]],
                              [[],[],[],[],[],[],[],[]],
                              ]    
        
        for i in range(len(dates)):
            if i > 0:
                for division in range(len(groupTms)):
                    for team in groupTms[division]:
                        teamWins_pre,teamLosses_pre,teamTies_pre = standings.period_standings(results_conf,dates,3,i,team)
                        
                        # print([team,[teamWins_pre,teamLosses_pre,teamTies_pre]])
                        if i > 1:
                            teamWins_wu,teamLosses_wu = standings.upToPoint_standings(WU_Results, dates, 6, i-1,team)
                            # print([teamWins_wu,teamLosses_wu,teamTies_wu])
                            teamWins_post,teamLosses_post = standings.upToPoint_standings(results_conf_final,dates,3,i-1,team)
                            # print([teamWins_post,teamLosses_post,teamTies_post])
                            teamWins_pre += teamWins_wu
                            teamWins_pre += teamWins_post
                            
                            teamLosses_pre += teamLosses_wu
                            teamLosses_pre += teamLosses_post
                            # print([team,[teamWins_pre,teamLosses_pre,teamTies_pre],
                            #    [teamWins_wu,teamLosses_wu,teamTies_wu]])
                        
                        try:
                            winPct_pre = round(teamWins_pre/(teamWins_pre+teamLosses_pre),3)
                        except ZeroDivisionError:
                            winPct_pre = None
                        WUpre_Standings[i-1][division].append([team ,teamWins_pre,teamLosses_pre,teamTies_pre,winPct_pre])
                        
                        
                        
                        
                        teamWins_post,teamLosses_post = standings.upToPoint_standings(results_conf_final,dates,3,i,team)
                        teamWins_wu,teamLosses_wu = standings.upToPoint_standings(WU_Results,dates,6,i,team)
                        teamWins_post += teamWins_wu
                        teamLosses_post += teamLosses_wu
                        try:
                            winPct_post = round(teamWins_post/(teamWins_post+teamLosses_post),3)
                        except ZeroDivisionError:
                            winPct_post = None
                        WUpost_Standings[i-1][division].append([team ,teamWins_post,teamLosses_post,0,winPct_post])

        WUpre_Standings = [[sorted(group, key=itemgetter(4), reverse=True) for group in x] for x in WUpre_Standings]
        WUpost_Standings = [[sorted(group, key=itemgetter(4), reverse=True) for group in x] for x in WUpost_Standings]
        
        return WUpre_Standings,WUpost_Standings
        
    
    def standingLists(WUpre_Standings,WUpost_Standings,leagueFormat):
        ## Create standings list
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
        
        return standingParts