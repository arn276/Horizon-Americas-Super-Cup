SELECT --sum(outs_wu)
	distinct conference, gamedate, hometeam, awayteam, regulationresult, homescore_reg, awayscore_reg, wrapupresult, homescore_wu, awayscore_wu, outs_wu, simnumber
	FROM seasons.results
	where 1=1 
		-- and gamedate <'5/6/2010' and  wrapupresult != ''
		-- and simnumber	= 165 and hometeam in ('Montreal','New Haven', 'Boston','New York', 'Detroit','Indianapolis', 'Akron','Columbus')
		-- and simnumber	= 220 and hometeam in ('Philadelphia','Pittsburgh', 'Toronto','Washington, D.C.', 'Detroit','Indianapolis', 'Akron','Columbus')
		-- and simnumber = 309 and hometeam in ('Philadelphia','Pittsburgh', 'Toronto','Washington, D.C.', 'Detroit','Indianapolis', 'Akron','Columbus')
		-- and simnumber = 330 and hometeam in ('Dallas','San Antonio', 'Monterrey','Merida', 'Calgary','Vancouver', 'Denver','Seattle')
		and simnumber = 87 and gamedate >'8/15/2010' and wrapupresult != '' and hometeam in ('Birmingham','Nashville','Atlanta','Charlotte','Oakland','Los Angeles', 'Phoenix','Tijuana') 
		
		-- and gamedate >'8/15/2010' and wrapupresult != '' and (hometeam = 'Phoenix' or awayteam = 'Phoenix');
		-- and gamedate >'7/1/2010' and gamedate <'8/15/2010' and wrapupresult != '' and (hometeam = 'Philadelphia' or awayteam = 'Philadelphia')
		 
		-- and hometeam in ('Philadelphia','Washington, D.C.', 'Pittsburgh','Toronto', 'Winnipeg','St. Paul', 'St. Louis','Chicago')
		-- and hometeam in ('Nashville','Charlotte', 'Atlanta','Birmingham', 'Oakland','Los Angeles', 'Phoenix','Tijuana')
		-- and hometeam in ('Dallas','San Antonio', 'Monterrey','Merida', 'Calgary','Vancouver', 'Denver','Seattle')