import copy, random


class simulate():
    def teamStrength(conferenceTms,rankAvgWinPct):
        '''
        Parameters
        ----------
        conferenceTms: list of all team sin conference
        rankAvgWinPct: average MLB historic winning percent (since 1969) by conference rank
        
        Function: Randomly assign team stength (historic winning percent) to each team 
                    for simulating HASC results
        
        Returns
        -------
        teamStength: List of teams and assigned team strength 

        '''
        conf = copy.deepcopy(conferenceTms)
        teamStength = []
        for i in range(len(rankAvgWinPct)):
            for stength in rankAvgWinPct[i][1:]:
                team = random.choice(conf[i])
                conf[i].remove(team)
                teamStength.append([team,stength])
        return teamStength
    
    
    def win_loss(schedule, teamStength, extrasRate, scoringDic,seasons_exOuts,homefield = 0,tie=None):
        '''
        Parameters
        ----------
        schedule: Conference schedule by dates
        teamStength: List of teams and assigned team strength
        extrasRate: rate of MLB games that go extra innings
        scoringDic: Dicitonary of results: home/road result options and odds of outcomes, including for extras.
        seasons_exOuts: DF of MLB extra-inning games, for number of outs post zombie runner change
        homefield: homefield advantage % (default - 0%)
        tie: If game was tie at end of regulation signals different process for simulating wind-up
        
        Function: randomise win-loss of every league game in league schedule
        
        Returns
        -------
        results_conf: Conference results for the season.
        '''
        results_conf=[]
        for game in schedule:
            if game[1] == '':
                results_conf.append(game+[''])
            else:
                hometeam,awayteam = simulate.teams(game)
                
                # Find home-away weight 
                homeWt = simulate.teamWeight(teamStength, hometeam)
                awayWt = simulate.teamWeight(teamStength, awayteam)
                
                # Balance to 100% odds
                totalStrgthWt = homeWt+awayWt
                adj = 100/totalStrgthWt
                homeWt,awayWt = homeWt*adj,awayWt*adj
                
                # change for for home field advantage
                homeWt,awayWt = homeWt+homefield,awayWt-homefield
                
                # Change for tie at end of regulation
                extras =[]
                if tie is not None:
                    homeWt,awayWt = homeWt-(extrasRate/2),awayWt-(extrasRate/2)
                    # Result weight based selection
                    winnerSelection = random.choices(game[1:]+['Tie in regulation'], weights=(homeWt, awayWt,extrasRate), k=1)
                    # Add Score
                    score = simulate.reg_scores(winnerSelection,hometeam,awayteam,scoringDic)
                    results_conf.append(game+winnerSelection+score[0])
                else:
                    # Result weight based selection
                    winnerSelection = random.choices(game[1:3], weights=(homeWt, awayWt), k=1)
                    # Add Score
                    score = simulate.ex_scores(winnerSelection,hometeam,awayteam,scoringDic,int(game[4]))
                    extras = random.choices(seasons_exOuts['lengthofgame_outs'], weights=(seasons_exOuts['PercentOfTotal']), k=1)
                    
                    results_conf.append(game+winnerSelection+score[0]+extras)
                    
        return results_conf
    
    
    def teams(game):
        '''
        Parameters
        ----------
        game : List of game details

        Returns
        -------
        Home Team Name 
        Road Team Name
        '''
        return game[1], game[2]
    
    
    def teamWeight(teamStength, team):
        '''
        Parameters
        ----------
        teamStength:  List of teams and assigned team strength
        team: Team name

        Returns
        -------
        Team stength (winning percent on paper)

        '''
        return [weight[1]*100 for weight in teamStength if weight[0] == team][0]   
    
    
    def reg_scores(winnerSelection,hometeam,awayteam,scoringDic):
        '''
        Parameters
        ----------
        winnerSelection: Winning team
        hometeam: Home team name
        awayteam: Road team name
        scoringDic: Dicitonary of results: home/road result options and odds of outcomes, including for extras.
            
        Function: random selection of game score for season games completed in regulation

        Returns
        -------
        score: game scores
        '''
        if hometeam == winnerSelection[0]:
            score = random.choices(scoringDic['home_RsltOptions'], weights=(scoringDic['home_odds']), k=1)
        elif awayteam == winnerSelection[0]:
            score = random.choices(scoringDic['road_RsltOptions'], weights=(scoringDic['road_odds']), k=1)
        else:
            score = [random.choices(scoringDic['extraScores'], weights=(scoringDic['extra_odds']), k=1)]
            score[0] += score[0]
        return score
    
    
    def ex_scores(winnerSelection,hometeam,awayteam,scoringDic,regScore):
        '''
        Parameters
        ----------
        winnerSelection: Winning team
        hometeam: Home team name
        awayteam: Road team name
        scoringDic: Dicitonary of results: home/road result options and odds of outcomes, including for extras.
        regScore: game score at end of regulation

        Function: Selecting extra innings score in the wind-up

        Returns
        -------
        score: Final score
        '''
        homeOptions = scoringDic['home_ExRsltOptions']
        homeWeights = scoringDic['home_ExOdds']
        homeOptionsAdj,homeWeightsAdj = simulate.adjOptionsWU(homeOptions, homeWeights,regScore)
                
        awayOptions = scoringDic['road_ExRsltOptions']
        awayWeights = scoringDic['road_ExOdds']
        awayOptionsAdj,awayWeightsAdj = simulate.adjOptionsWU(awayOptions, awayWeights,regScore)
        
        if hometeam == winnerSelection[0]:
            score = random.choices(homeOptionsAdj, weights=(homeWeightsAdj), k=1)
        elif awayteam == winnerSelection[0]:
            score = random.choices(awayOptionsAdj, weights=(awayWeightsAdj), k=1)
            
        return score
    
    def adjOptionsWU(options, weights,regScore):
        '''
        Parameters
        ----------
        options: possible score results for team in wind-up
        weights: weights of possible score outcomes
        regScore: game score at end of regulation
            
        Function: Adjusting wind-up results option tables, based on end of regulation scores

        Returns
        -------
        optionsAdj : filtered possible wind-up score results
        weightsAdj : filtered possible wind-up result odds
        '''
        optionsAdj,weightsAdj =[],[]
        for x in range(len(options)):
            h = options[x][0]
            a = options[x][1]
            
            if (h >= regScore and h <= regScore+2 and a >= regScore) or (h >= regScore and a >= regScore and a <= regScore+2):
                optionsAdj.append(options[x])
                weightsAdj.append(weights[x])
        return optionsAdj,weightsAdj
    
    
    def WU_createResults(results_conf, dates, teamStength, extrasRate, scoringDic, seasons_exOuts):
        '''
        Parameters
        ----------
        results_conf: season game results for the entire conference
        dates: list of start of date and all wind-up dates
        teamStength: List of teams and assigned team strength
        extrasRate: rate of MLB games that go extra innings
        scoringDic: Dicitonary of results: home/road result options and odds of outcomes, including for extras.
        seasons_exOuts: DF of MLB extra-inning games, for number of outs post zombie runner change
                
        Function: selection of win-loss results for games in the Wind-up
            
        Returns
        -------
        WU_Results: List results of the Wind-up

        '''
        WU_Results = []
        for i in range(len(dates)):
            if i > 0:
                schedule_wu = [x for x in results_conf if x[3] == 'Tie in regulation' 
                                  and x[0]>=dates[i-1] and x[0]<dates[i]]
                sim = simulate.win_loss(schedule_wu, teamStength, extrasRate, scoringDic, seasons_exOuts)
                WU_Results.append(sim)
        return WU_Results
    
    
    def seasonResultsOrder(results_conf,WU_Results, dates):
        '''
        Parameters
        ----------
        results_conf: season game results for the entire conference
        WU_Results: List results of all the Wind-ups
        dates: List of start of date and all wind-up dates

        Function: Combining the results of the regular season and the wind-ups

        Returns
        -------
        resultsOrder : Combined season and wind-up resuts

        '''
        resultsOrder = []
        for i in range(len(dates)):
            if i > 0:
                complete = [x for x in results_conf if x[3] != 'Tie in regulation' and x[0]>=dates[i-1] and x[0]<dates[i]]
                WU_rd = [x for x in WU_Results if x[0]>=dates[i-1] and x[0]<dates[i]]
                resultsOrder = resultsOrder+complete+WU_rd
        return resultsOrder
    
    