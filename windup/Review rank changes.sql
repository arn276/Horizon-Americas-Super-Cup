SELECT r.simnumber, r.conference, r.division, r.teamgroup, r.team, 
		prewu1rank, postwu1rank, prewu2rank, postwu2rank, prewu3rank, postwu3rank, prewu4rank, postwu4rank
	FROM seasons.rankchanges as r
	where 1=1
		-- and teamgroup = 'Rush Group' and r.simnumber = 330
		--and team  = 'Phoenix' 
		--and (prewu4rank = 1 or postwu4rank = 1)
		and simnumber = 330