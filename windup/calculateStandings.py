# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 19:56:12 2025

@author: aaron
"""

from operator import itemgetter

class standings():
    def WU_Standings(results_conf, groups, dates, winnerCol, WUpre_Standings):
        for i in range(len(dates)):
            if i > 0:
                for division in range(len(groups)):
                    for team in groups[division]:
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
                    
        return WUpre_Standings
    
    
    def finalStandingsSummary(WUpre_Standings,WUpost_Standings):
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
        return WUpost_Standings