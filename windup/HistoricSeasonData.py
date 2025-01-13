# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 10:31:28 2025

@author: aaron
"""
import pandas as pd
import statsapi, csv
from collections import Counter
from League_Info import leagueFormation

class historicSeasons():
    def readSeason(locationStr):
        columns = ['gamedate','numberofgames','dayofweek',
                    'roadtm','roadlg','roadtmgamenum',
                    'hometm','homelg','hometmgamenum',
                    'roadscor','homescore','lengthofgame_outs','dayornight',
                    'completioninformation','forfeit','protest',
                    'parkid','attendance',
                    'timeofgame_min','roadlinescore','homelinescore',
                    'roadab','roadh','roaddouble','roadtriple','roadhr','roadrbi',
                    'roadsachit','roadsacfly','roadhbp','roadbb','roadibb',
                    'roadstrikeout','roadsb','roadcs','roadgdp','roadcatcherint',
                    'roadlob','roadpitcherused','roadinder','roadteamer',
                    'roadwp','roadbalk','roadputout','roadassists','roaderrors',
                    'roadpb','roaddoubleplay','roadtripleplay',
                    'homeab','homeh','homedouble','hometriple','homehr','homerbi',
                    'homesachit','homesacfly','homehbp','homebb','homeibb',
                    'homestrikeout','homesb','homecs','homegdp','homecatcherint',
                    'homelob','homepitcherused','homeinder','hometeamer',
                    'homewp','homebalk','homeputout','homeassists','homeerrors',
                    'homepb','homedoubleplay','hometripleplay',
                    'ump_homeid','ump_homename','ump_1bid','ump_1bname',
                    'ump_2bid','ump_2bname','ump_3bid','ump_3bname',
                    'ump_lfid','ump_lfname','ump_rfid','ump_rfname',
                    'road_mgrid','road_mgrname','home_mgrid','home_mgrname',
                    'winningpitcherid','winningpitchername','losingpitcherid','losingpitchername',
                    'savingpitcherid','savingpitchername','gamewinningrbibatterid','gamewinningrbibattername',
                    'road_spid','road_spname','home_spid','home_spname',
                    'road_bat1id','road_bat1name','road_bat1pos',
                    'road_bat2id','road_bat2name','road_bat2pos',
                    'road_bat3id','road_bat3name','road_bat3pos',
                    'road_bat4id','road_bat4name','road_bat4pos',
                    'road_bat5id','road_bat5name','road_bat5pos',
                    'road_bat6id','road_bat6name','road_bat6pos',
                    'road_bat7id','road_bat7name','road_bat7pos',
                    'road_bat8id','road_bat8name','road_bat8pos',
                    'road_bat9id','road_bat9name','road_bat9pos',
                    'home_bat1id','home_bat1name','home_bat1pos',
                    'home_bat2id','home_bat2name','home_bat2pos',
                    'home_bat3id','home_bat3name','home_bat3pos',
                    'home_bat4id','home_bat4name','home_bat4pos',
                    'home_bat5id','home_bat5name','home_bat5pos',
                    'home_bat6id','home_bat6name','home_bat6pos',
                    'home_bat7id','home_bat7name','home_bat7pos',
                    'home_bat8id','home_bat8name','home_bat8pos',
                    'home_bat9id','home_bat9name','home_bat9pos',
                    'additionalinfo','acquisitioninfo']
        seasonResults = pd.read_csv(locationStr, names= columns,
                                    usecols = ['gamedate','roadtm','hometm',
                                               'roadscor','homescore','lengthofgame_outs',
                                               'roadlinescore','homelinescore'])
        return seasonResults
    
    def formatHistoricSeason():
        base = 1969
        yearLst = []
        for i in range(2024-base+1):
            yearLst.append(base+i)

        # Collect all standings in statsApi
        allStandings = []
        leagueIds = [103,104]
        for league in leagueIds:
            for year in yearLst:
                standings = []
                try: # Data by season and league, keeping only team lines, split each field
                    season = statsapi.standings(leagueId=league,season=str(year))
                    standing = [x for x in season.split('\n') if x[:4] not in ['Nati','Amer','Rank'] and x != '']
                    splitToElements = [x.split(' ') for x in standing]
            
                    # Keep only those fields with data
                    teamElements=[]
                    for team in splitToElements:
                        elements = [t.strip() for t in team[1:] if t not in ['','-','E']]
                        teamNumElements = []
                        teamname = ''
                        for e in elements:
                            try:
                                teamNumElements.append(int(e))
                            except ValueError:
                                try: float(e)
                                except ValueError:
                                    teamname += ' '+e
                        wins = teamNumElements[1]
                        losses = teamNumElements[2]
                        winPct = round(float(wins)/(float(wins)+float(losses)),3)
                        teamElements.append([year,league,teamname.strip(),wins,losses,winPct])
                    standings.append(teamElements)
                except KeyError:
                    standings.append([year, league])    
                allStandings.append(standings)
             
                
        # Store Historic Standings
        historicList = leagueFormation.flattenLsts(allStandings)
        historicList = leagueFormation.flattenLsts(historicList)
        with open(r'C:\Users\aaron\OneDrive\Documents\GitHub\historicStandings.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Year','League','Team','Wins','Losses', 'Winning Pct'])
            writer.writerows(historicList)
                             
    
    def historicScores():
        locationStr = r'C:\Users\Public\retrosheets\gl2020_23'
        season24 = historicSeasons.readSeason(locationStr+r'\gl2024.txt')

        # Score commonality
        regulation = season24[(season24['lengthofgame_outs']>=51) | (season24['lengthofgame_outs']<=54) ]
        regulation.drop(columns = ['roadlinescore','homelinescore'])
        resultRate = regulation[['roadscor','homescore']].value_counts().reset_index()
        resultRate['PercentOfTotal'] = resultRate['count']/resultRate['count'].sum()

        resultRate.loc[resultRate['homescore'] > resultRate['roadscor'], 'winner'] = 'Home'
        resultRate.loc[resultRate['homescore'] < resultRate['roadscor'], 'winner'] = 'Road'

        # rate of going to extras
        extras = season24[season24['lengthofgame_outs']>54]
        extrasRate = round(len(extras)/len(season24),3)*100
        
        # Rates for result of extras
        extras.drop(columns = ['roadlinescore','homelinescore'])
        extrasResultRate = extras[['roadscor','homescore']].value_counts().reset_index()
        extrasResultRate['PercentOfTotal'] = extrasResultRate['count']/extrasResultRate['count'].sum()
        
        extrasResultRate.loc[extrasResultRate['homescore'] > extrasResultRate['roadscor'], 'winner'] = 'Home'
        extrasResultRate.loc[extrasResultRate['homescore'] < extrasResultRate['roadscor'], 'winner'] = 'Road'
        
        return extras, extrasRate,resultRate,extrasResultRate
        
        
    def summarizeStandings(historicList, resultRate, extras, extrasResultRate):
        years = list(set([int(year[0]) for year in historicList[1:]]))
        lgIds = list(set([lg[1] for lg in historicList[1:]]))

        allStandings = []
        for y in years:
            season = [s for s in historicList if s[0]==str(y)]
            for l in lgIds:
                allStandings.append([t for t in season if t[1]==str(l)])


        # Mock winning percents 
        yearlyWinPct = []
        for year in allStandings:
            winpct = [float(team[5]) for team in year]
            avgWinPct = sum(winpct)/len(winpct)
            while len(winpct)<16:
                winpct.append(avgWinPct)
            winpct.sort(reverse=True)
            yearlyWinPct.append([int(year[0][0])]+[int(year[0][1])]+winpct)  

        # Find average league rank winning percent
        # will use to simulate team strength
        rankAvgWinPct = []
        for lg in lgIds:
            league = [lg]
            for i in range(16):
                rankWinPct = [x[i+2] for x in yearlyWinPct[-3:] if x[1]==int(lg)]
                avgWinPct = round(sum(rankWinPct)/len(rankWinPct),3)
                league.append(avgWinPct)
            rankAvgWinPct.append(league)
            
        # Convert historic game score commonality to list
        # Creating lists for random result selections
        scoreOptions_reg = resultRate.values.tolist()
        home_RsltOptions = [[x[1],x[0]] for x in scoreOptions_reg if x[4] == 'Home']
        home_odds = [round(x[3]*100,3) for x in scoreOptions_reg if x[4] == 'Home']
        road_RsltOptions = [[x[1],x[0]] for x in scoreOptions_reg if x[4] == 'Road']
        road_odds = [round(x[3]*100,3) for x in scoreOptions_reg if x[4] == 'Road']

        # Creating list of unique scores and common rates for ties
        scoreOptions_ex = extras.values.tolist()
        regulationScores = []
        for game in scoreOptions_ex:
            score_rd = []
            for inn in game[6][:9]:score_rd.append(int(inn)) 
            score_hm = []
            for inn in game[7][:9]:score_hm.append(int(inn)) 
            if sum(score_rd) == sum(score_hm):
                regulationScores.append(sum(score_rd))
            else:
                print(game)
            
        uniqueScores = list(Counter(regulationScores).keys())
        occuranceCount = list(Counter(regulationScores).values())

        extra_odds = []
        for i in range(len(uniqueScores)):
            extra_odds.append( round((occuranceCount[i]/sum(occuranceCount))*100,2))
        
        # Creating list of unique scores and common rates for tie results
        scoreResults_ex = extrasResultRate.values.tolist()
        home_ExRsltOptions = [[x[1],x[0]] for x in scoreResults_ex if x[4] == 'Home']
        home_ExOdds = [round(x[3]*100,3) for x in scoreResults_ex if x[4] == 'Home']
        road_ExRsltOptions = [[x[1],x[0]] for x in scoreResults_ex if x[4] == 'Road']
        road_ExOdds = [round(x[3]*100,3) for x in scoreResults_ex if x[4] == 'Road']
       
        scoringDic = {'home_RsltOptions':home_RsltOptions,
                      'home_odds':home_odds,
                      'road_RsltOptions':road_RsltOptions,
                      'road_odds':road_odds,
                      'extraScores':uniqueScores,
                      'extra_odds':extra_odds,
                      'home_ExRsltOptions':home_ExRsltOptions,
                      'home_ExOdds':home_ExOdds,
                      'road_ExRsltOptions':road_ExRsltOptions,
                      'road_ExOdds':road_ExOdds}
        
        return rankAvgWinPct, scoringDic
        
        
        
        
        
        
        
        