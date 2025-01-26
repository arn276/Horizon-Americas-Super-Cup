import copy, datetime, random

class schedule:    
    def createOrderOfGames(AllMatchups):
        '''
        Parameters
        ----------
        AllMatchups : List of all the matchups
            
        Function: Order series based on group, conference 1, division, conference 2 
                    for series type in order
        Returns
        -------
        conf1 : Schedule order for Founders Conference
        conf2 : Schedule order for Visionaries Conference
        '''
        seriesOrder = [
                        ['g','g','g','g','g','g','c1','c1','c1','c1'],
                       ['d','d','d','d','d','d','d','d','d','d','d','d','d','d','d','d'],
                       ['g','g','g','g','c2','c2','c2','c2','c2','c2','c2','c2'],
                       ['g','g','g','g','c1','c1','c1','c1','g','g','g','g']
                       ]
        matchupsForScheduling = copy.deepcopy(AllMatchups)
        conf1 = schedule.scheduleGames(seriesOrder,matchupsForScheduling,0,2,4,6)
        conf2 = schedule.scheduleGames(seriesOrder,matchupsForScheduling,1,3,5,7)
        return conf1,conf2
        

    def scheduleGames(seriesOrder,matchupsForScheduling,group,division,conf1,conf2):
        '''
        Parameters
        ----------
        seriesOrder: Set order of series type of matchups
        matchupsForScheduling: Order of series matchups by type (in-group, g vs div g, g vs in conf g1, g vs in conf g2)
        group: group section of matchupsForScheduling 
        division: division section of matchupsForScheduling 
        conf1: conference pair 1 section of matchupsForScheduling 
        conf2: conference pair 2 section of matchupsForScheduling 

        Function: schedues each game of all series in order

        Returns
        -------
        confSchedule: Schedule order of all games
        '''
        confSchedule=[]
        for q in range(len(seriesOrder)):
            for s in seriesOrder[q]:
                days = [[],[],[]]
                if s == 'g': pair = group
                if s == 'd': pair = division
                if s == 'c1': pair = conf1
                if s == 'c2': pair = conf2
                roundMatchups = copy.deepcopy(matchupsForScheduling[pair][0]) ## This round matchups
                matchupsForScheduling[pair].remove(roundMatchups) ## Remove from list
                for game in roundMatchups:
                    gameNo = 3
                    while gameNo>0:
                        gameNo -= 1
                        days[gameNo].append([game[0],game[1]])
                confSchedule.append(days) 
            if q == 1: confSchedule.append([[],[],[],[]])
            else: confSchedule.append([[],[],[]])
        return confSchedule


    def setDates(conf,base):
        '''
        Parameters
        ----------
        conf : order of games for conference
        base : base start date for season

        Function: assigning dates to order of games.

        Returns
        -------
        schedules : schedule by dates
        '''
        date_list = [base + datetime.timedelta(days=x) for x in range(225)] ##185
        schedules = []
        for series in range(len(conf)):
            for leagueGame in range(len(conf[series])):
                if len(conf[series][leagueGame]) == 0:
                    ## Setting blank days for wind-up
                    if len([date[1] for date in schedules if date[0] == date_list[0]])>1 : del date_list[0]
                    schedules.append([date_list[0]]+['',''])
                    del date_list[0]
                else:
                    for game in range(len(conf[series][leagueGame])):
                        prevDayTeams = [date[1] for date in schedules if date[0] == date_list[0]]+[date[2] for date in schedules if date[0] == date_list[0]]
                        homechk = conf[series][leagueGame][game][0] in prevDayTeams
                        awaychk = conf[series][leagueGame][game][1] in prevDayTeams
                        # Check to build in off days by offsetting series start by a day
                        if game <5 and homechk == False and awaychk == False: 
                            schedules.append([date_list[0]]+conf[series][leagueGame][game])
                        else: schedules.append([date_list[1]]+conf[series][leagueGame][game])
                    del date_list[0]
            if series != len(conf)-1:
                if len(conf[series+1][0]) != 0 and len(conf[series-1][0]) and len(conf[series][0])!= 0 and series%3==0:
                    del date_list[0]
        return schedules
    
    
    def groupSeriesToMake4Games(base,schedules,groupTms):
        '''
        Parameters
        ----------
        base: base start date for season
        schedules: schedule of games by dates
        groupTms: List of lists of all teams in a group

        Function: Find off day for each in-group matchup (home and away) to add a 4th game to series

        Returns
        -------
        schedules : schedule by dates
        '''
        ## season game date list
        date_list = [base + datetime.timedelta(days=x) for x in range(186)]
        excludionLst = [d[0] for d in schedules if d[1] == '']
        maxDt = max([d[0] for d in schedules if d[1] != ''])
        date_list = [d for d in date_list if d not in excludionLst and d < maxDt]

        for group in groupTms: 
            #List all group games by group
            groupGames = [game for game in schedules if game[1] in group and game[2] in group]
            #Find unique
            uniqueLst = []
            for matchup in [[game[1],game[2]] for game in groupGames]:
                if matchup not in uniqueLst: uniqueLst.append(matchup)
            #Find dates team could extend series
            for matchup in uniqueLst:
                ## date where both teams have back to back days off
                FourthGmOption = []
                homeTmPairOff = schedule.findBackToBackOff(schedules,matchup[0],date_list)
                awayTmPairOff = schedule.findBackToBackOff(schedules,matchup[1],date_list)
                pairedOffPriority = [date for date in homeTmPairOff if date in awayTmPairOff]
                # Dates They Already Play
                checkDates = [date[0] for date in schedules if date[1] == matchup[0] and date[2] == matchup[1]]
                for date in checkDates:
                    if date != base:
                        # Check if both teams have a shared team off before series
                        prevDt = date+datetime.timedelta(days=-1)
                        prevDayTeams = [match[1] for match in schedules if match[0] == prevDt]+[match[2] for match in schedules if match[0] == prevDt]
                        homechk = matchup[0] in prevDayTeams
                        awaychk = matchup[1] in prevDayTeams
                        if homechk == False and awaychk == False:
                            FourthGmOption.append(prevDt)
                    
                    # Check if both teams have a shared team off after series
                    tomorrow = date+datetime.timedelta(days=1) 
                    tomorrowTeams = [match[1] for match in schedules if match[0] == tomorrow]+[match[2] for match in schedules if match[0] == tomorrow]
                    homechk = matchup[0] in tomorrowTeams
                    awaychk = matchup[1] in tomorrowTeams
                    if homechk == False and awaychk == False:
                        FourthGmOption.append(tomorrow)
                #Verify list of shared open days aren't days they already play or days for the quarterly wind-up
                FourthGmOption = [date for date in FourthGmOption if date not in excludionLst and date not in checkDates]
                
                # Check if the both teams have a day off next to one of them having two days off
                if len([date for date in FourthGmOption if date in pairedOffPriority]) >0:
                    priorityDate = max([date for date in FourthGmOption if date in pairedOffPriority])
                    schedules.append([priorityDate]+matchup)
                # Find Latest shared open date next to series to play 10th game
                elif len(FourthGmOption)>0:
                    schedules.append([max(FourthGmOption)]+matchup)
                # Schedule doubleheader
                else:
                    minDt, maxDt = datetime.date(2010, 5, 1),datetime.date(2010, 9, 1)
                    doubleHeader = random.choice([game for game in groupGames 
                                                  if game[0]> minDt and game[0]<maxDt and 
                                                  game[1] == matchup[0] and game[2] == matchup[1]])
                    schedules.append(doubleHeader)
        return schedules
    
    
    
    def findBackToBackOff(schedules,team,date_list):
        '''
        Parameters
        ----------
        schedules: schedule of games by dates
        team: team to search
        date_list: available dates in season
        
        Function: find when a team has back-to-back off days

        Returns
        -------
        backToBackOpen: List of back-to-back open dates for team
        '''
        backToBackOpen = []
        # Days team plays
        teamDates = [date[0] for date in schedules if date[1] == team or date[2] == team]
        # Days team doesn't play
        teamDates = [d for d in date_list if d not in  teamDates]
        for date in range(len(teamDates)):
            if date != 0:
                if abs((teamDates[date] - teamDates[date-1]).days) == 1:
                    backToBackOpen.append(teamDates[date])
                    backToBackOpen.append(teamDates[date-1])
        return backToBackOpen
    
    
    
    