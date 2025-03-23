import csv
from operator import itemgetter

class standings():
    def createStandings(results_conf,WU_Results,results_conf_final,dates,groupTms):
        '''
        Parameters
        ----------
        results_conf: Results of the conference games
        WU_Results: List results of all the Wind-ups
        results_conf_final: End of season results, with all Wind-up results completed
        dates: list of start of date and all wind-up dates
        groupTms: List of lists of all teams in a group

        Function: Create standings for each Wind-up, pre- and post-Wind-up

        Returns
        -------
        WUpre_Standings: Standings prior to each Wind-up
        WUpost_Standings : Standings after each Wind-up
        '''
        ## Calculate Standings
        WUpre_Standings = standings.emptyStandingsLists()
        WUpost_Standings = standings.emptyStandingsLists() 
        
        for i in range(len(dates)):
            if i > 0:
                for division in range(len(groupTms)):
                    for team in groupTms[division]:
                        teamWins_pre,teamLosses_pre,teamTies_pre = standings.period_standings(results_conf,dates,3,i,team)
                        if i > 1:
                            teamWins_wu,teamLosses_wu = standings.upToPoint_standings(WU_Results, dates[i-1], 6, team)
                            teamWins_post,teamLosses_post = standings.upToPoint_standings(results_conf_final,dates[i-1],3,team)
                            teamWins_pre += teamWins_wu
                            teamWins_pre += teamWins_post
                            
                            teamLosses_pre += teamLosses_wu
                            teamLosses_pre += teamLosses_post
                        
                        try:
                            winPct_pre = round(teamWins_pre/(teamWins_pre+teamLosses_pre),3)
                        except ZeroDivisionError:
                            winPct_pre = None
                        WUpre_Standings[i-1][division].append([team ,teamWins_pre,teamLosses_pre,teamTies_pre,winPct_pre])
                        
                        teamWins_post,teamLosses_post = standings.upToPoint_standings(results_conf_final,dates[i],3,team)
                        teamWins_wu,teamLosses_wu = standings.upToPoint_standings(WU_Results,dates[i],6,team)
                        teamWins_post += teamWins_wu
                        teamLosses_post += teamLosses_wu
                        try:
                            winPct_post = round(teamWins_post/(teamWins_post+teamLosses_post),3)
                        except ZeroDivisionError:
                            winPct_post = None
                        WUpost_Standings[i-1][division].append([team ,teamWins_post,teamLosses_post,0,winPct_post])
        
        ## sorting group standings by winning percent
        WUpre_Standings = [[sorted(group, key=itemgetter(4), reverse=True) for group in x] for x in WUpre_Standings]
        WUpost_Standings = [[sorted(group, key=itemgetter(4), reverse=True) for group in x] for x in WUpost_Standings]
        
        return WUpre_Standings,WUpost_Standings
        
    
    def emptyStandingsLists():
        '''
        Returns
        -------
        lst : Empty list for group standings for each Wind-up 

        '''
        lst = [ [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[]],
               ]
        return lst
    
    
    def period_standings(results_conf, dates, winnerCol, i, team):
        '''
        Parameters
        ----------
        results_conf: Results of the conference games
        dates: list of start of date and all wind-up dates
        winnerCol: Column number with the winning team name
        i: count in windups date list we are on
        team: Team for whose standing is being calculated

        Function: Calculating standings up to start of Wind-up

        Returns
        -------
        teamWins_pre: Total team wins up to start of Wind-up
        teamLosses_pre: Total team losses up to start of Wind-up
        teamTies_pre: Total team ties at end of regulation up to start of Wind-up

        '''
        teamWins_pre = len([x for x in results_conf if x[winnerCol] == team 
                       and x[0]>=dates[i-1] 
                       and x[0]<=dates[i] ])
        teamLosses_pre = len([x for x in results_conf if (x[1] == team  or x[2] == team ) 
                          and x[winnerCol] != team and x[winnerCol] != 'Tie in regulation' 
                          and x[0]>=dates[i-1] 
                          and x[0]<=dates[i]])
        teamTies_pre = len([x for x in results_conf if (x[1] == team  or x[2] == team ) 
                          and x[winnerCol] == 'Tie in regulation' 
                          and x[0]>=dates[i-1] 
                          and x[0]<=dates[i]])
        return teamWins_pre,teamLosses_pre,teamTies_pre
    
    
    def upToPoint_standings(results_conf, date, winnerCol, team):
        '''
        Parameters
        ----------
        results_conf: Results of the conference games
        date: date to calculate standings through
        winnerCol: Column number with the winning team name
        team: Team for whose standing is being calculated
        
        Function: Calculate standings up to date of Wind-up

        Returns
        -------
        teamWins_post : Team wins through the end of Wind-up date
        teamLosses_post : Team losses through the end of Wind-up date
        '''
        # print(team)
        # print(winnerCol)
        # print(date)
        # print(results_conf[12])
        # print([x for x in results_conf if x[winnerCol] == team  ])
        # print([x for x in results_conf if  x[0]<=date ])
        teamWins_post = len([x for x in results_conf if x[winnerCol] == team and x[0]<=date ])
        teamLosses_post = len([x for x in results_conf if (x[1] == team  or x[2] == team ) 
                          and x[winnerCol] != team and x[winnerCol] != 'Tie in regulation' 
                          and x[0]<=date ])
        return teamWins_post,teamLosses_post
    
    
    def standingLists(WUpre_Standings,WUpost_Standings,leagueFormat):
        '''
        Parameters
        ----------
        WUpre_Standings: Standings prior to each Wind-up
        WUpost_Standings: Standings after each Wind-up
        leagueFormat: List - conference name, division name, group name, [teams in group]
        
        Function: Create final single list of standings for export
        
        Returns
        -------
        standingParts: final single list of standings for export

        '''
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
        
        return standingParts
    
    
    def rankStandings(standingParts,teamStength):
        '''
        Parameters
        ----------
        standingParts : final single list of standings for export

        Returns
        -------
        standings : final single list of standings for export with a division rank field
                    and the team strength rating
        '''
        standings = []
        for i in range(len(standingParts)):
            # Set rank 1-4, unles same percent as team above, then match.
            if (i+1)%4 == 0 : 
                if i == 0:  rank = 4
                elif standingParts[i][9] == standingParts[i-1][9]: rank = i%4
                else: rank = 4
            elif standingParts[i][9] == standingParts[i-1][9]: rank = i%4
            else: rank = (i+1)%4
            
            # Add team strength setting to compair to winning percent
            ts = [ts[1] for ts in teamStength if ts[0] == standingParts[i][5]]
            
            standings.append(standingParts[i][:5]+[rank]+standingParts[i][5:]+ts)
        return standings
            
            
            
            