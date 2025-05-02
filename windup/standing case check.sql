SELECT simnumber, standingsdate, timing, seasonpart, conference, division, teamgroup, standingrank, team, wins, losses, tiestofinish, winningpct, teamstrength
	FROM seasons.standings
	where 
		-- simnumber = 165 and seasonpart = 'Part 1'  and teamgroup in ('Port Group','Rail Group')
		-- simnumber = 220 and seasonpart = 'Part 1'  and teamgroup in ('Canal Group','Rail Group')
		-- simnumber = 309 and seasonpart = 'Part 1'  and teamgroup in ('Canal Group','Rail Group')
		-- simnumber = 330 and seasonpart = 'Part 1'  and teamgroup in ('Desert Group','Pass Group')
		
		simnumber = 201 and seasonpart = 'Part 4'  and teamgroup in ('Desert Group','Rush Group')
		-- simnumber = 87 and seasonpart = 'Part 1'  and teamgroup in ('Port Group','Aurora Group')
		
	-- order by 	tiestofinish
		
		-- and seasonpart = 'Part 4' and teamgroup = 'Rush Group';
		-- and seasonpart = 'Part 3' and teamgroup = 'Canal Group'
		