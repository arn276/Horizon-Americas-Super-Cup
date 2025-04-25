SELECT simnumber, standingsdate, timing, seasonpart, conference, division, teamgroup, standingrank, team, wins, losses, tiestofinish, winningpct, teamstrength
	FROM seasons.standings
	where simnumber = 220 
		-- and seasonpart = 'Part 1'  and teamgroup in ('Desert Group','Pass Group')
		and seasonpart = 'Part 4' and teamgroup = 'Rush Group';
		-- and seasonpart = 'Part 3' and teamgroup = 'Canal Group'
		