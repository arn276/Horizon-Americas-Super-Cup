# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 16:59:40 2025

@author: aaron
"""

import copy, random


class simulate():
    def teamStrength(conferenceTms,rankAvgWinPct):
        conf = copy.deepcopy(conferenceTms)
        teamStength = []
        for i in range(len(rankAvgWinPct)):
            for stength in rankAvgWinPct[i][1:]:
                team = random.choice(conf[i])
                conf[i].remove(team)
                teamStength.append([team,stength])
        
        return teamStength
    
    
    def teams(game):
        return game[1], game[2]
    
    
    def teamWeight(teamStength, team):
        return [weight[1]*100 for weight in teamStength if weight[0] == team][0]   
    
    
    def reg_scores(winnerSelection,hometeam,awayteam,scoringDic):
        if hometeam == winnerSelection[0]:
            score = random.choices(scoringDic['home_RsltOptions'], weights=(scoringDic['home_odds']), k=1)
        elif awayteam == winnerSelection[0]:
            score = random.choices(scoringDic['road_RsltOptions'], weights=(scoringDic['road_odds']), k=1)
        else:
            score = [random.choices(scoringDic['extraScores'], weights=(scoringDic['extra_odds']), k=1)]
            score[0] += score[0]
        return score
    
    
    def ex_scores(winnerSelection,hometeam,awayteam,scoringDic,regScore):
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
        optionsAdj,weightsAdj =[],[]
        for x in range(len(options)):
            h = options[x][0]
            a = options[x][1]
            if (h >= regScore and h <= regScore+1 and a >= regScore) or (h >= regScore and a >= regScore and a <= regScore+1):
                optionsAdj.append(options[x])
                weightsAdj.append(weights[x])
        return optionsAdj,weightsAdj
    
    
    def win_loss(schedule, teamStength, extrasRate, scoringDic,homefield = 0,tie=None):
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
                if tie is not None:
                    homeWt,awayWt = homeWt-(extrasRate/2),awayWt-(extrasRate/2)
                    # Result weight based selection
                    winnerSelection = random.choices(game[1:]+['Tie in regulation'], weights=(homeWt, awayWt,extrasRate), k=1)
                    # Add Score
                    score = simulate.reg_scores(winnerSelection,hometeam,awayteam,scoringDic)
                else:
                    # Result weight based selection
                    winnerSelection = random.choices(game[1:3], weights=(homeWt, awayWt), k=1)
                    # Add Score
                    score = simulate.ex_scores(winnerSelection,hometeam,awayteam,scoringDic,int(game[4]))
                
                results_conf.append(game+winnerSelection+score[0])
                
        return results_conf
    
    
    
    
    