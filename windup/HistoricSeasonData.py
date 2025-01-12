# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 10:31:28 2025

@author: aaron
"""
import pandas as pd
import statsapi, csv
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
        seasonResults = pd.read_csv(locationStr, names= columns,usecols = ['gamedate','roadtm','hometm','roadscor','homescore','lengthofgame_outs'])
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
                             
        
        
        
        
        
        
        
        
        
        
        
        