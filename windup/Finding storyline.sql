with drawImpact as (
	SELECT simnumber, conference, division, teamgroup, team, 
		prewu1rank, postwu1rank, prewu2rank, postwu2rank, prewu3rank, postwu3rank, prewu4rank, postwu4rank,
		
		case 
			when prewu1rank = postwu1rank then 1
			else 0
			end as NoChange
	FROM seasons.rankchanges
	
),

groupPairs as (
	select distinct r.simnumber,draw,home.teamgroup as keyGroup,away.teamgroup as oppoGroup
	FROM (select distinct simnumber,hometeam,awayteam,
				case
				when gamedate < '5/6/2010' then 'Part 1'
				when gamedate < '7/3/2010' then 'Part 2'
				when gamedate < '8/15/2010' then 'Part 3'
				else 'Part 4'
				end as draw
			FROM seasons.results) as r
	join seasons.standings as home on r.hometeam = home.team and r.simnumber = home.simnumber and r.draw = home.seasonpart and home.timing = 'pre Wind-up'
	join seasons.standings as away on r.awayteam = away.team and r.simnumber = away.simnumber and r.draw = away.seasonpart and away.timing = 'pre Wind-up'
	where 1=1 
		-- and gamedate <'5/6/2010' --and wrapupresult = ''
		and home.teamgroup != away.teamgroup
),


book1_stale as(
	select distinct d.simnumber, d.conference, d.division, d.teamgroup,
		-- d.team,prewu1rank, postwu1rank,tiestofinish,
		
		sum(NoChange)over(partition by d.simnumber, d.teamgroup) as stale,
		sum(tiestofinish)over(partition by d.simnumber, d.teamgroup) as totalties
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 1' and timing = 'pre Wind-up'
),

book1_stales as (
	select s.simnumber, conference, teamgroup, oppoGroup, totalties
	from book1_stale as s 
	left join groupPairs as gP on s.simnumber=gP.simnumber and s.teamgroup = gP.keyGroup and gP.draw = 'Part 1'
	where stale = 4
		-- and s.simnumber = 142 
),

book1 as(
	select distinct g1.simnumber as b1_sim, g1.conference as b1_conf, 
		case
		when g1.teamgroup > g1.oppoGroup then g1.oppoGroup
		else g1.teamgroup
		end as b1_group1, 
		
		case
		when g1.teamgroup < g1.oppoGroup then g1.oppoGroup
		else g1.teamgroup
		end as b1_group2, 
		
		(g1.totalties+g2.totalties)/2 as b1_totalDrawGames
	from book1_stales as g1
	inner join book1_stales as g2 on g1.oppoGroup = g2.teamgroup and g1.simnumber = g2.simnumber
),

book4_Pheonix as (
	select d.simnumber as b4_sim, 
		d.conference as b4_conference, 
		d.teamgroup as b4_teamGroup, 
		d.team as b4_team, 
		prewu4rank as b4_preDraw, 
		postwu4rank as b4_postDraw, 
		tiestofinish as b4_PheonixTies
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 4' and timing = 'pre Wind-up'
	where d.team ='Phoenix' and prewu4rank = 1 and postwu4rank != 1
		and s.seasonpart = 'Part 4' and s.timing = 'pre Wind-up'
		and tiestofinish>=4
),

book4_ties as(
	select distinct d.simnumber, d.conference, d.division, d.teamgroup,
		sum(tiestofinish)over(partition by d.simnumber, d.teamgroup) as totalties
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 4' and timing = 'pre Wind-up'
),

book4 as (
	select b4_sim, b4_conference, keyGroup as b4_group, oppogroup as b4_oppogroup, b4_PheonixTies, (keyTies.totalties+oppoTies.totalties)/2 as totalties
	from book4_Pheonix
	left join groupPairs on book4_Pheonix.b4_teamGroup = groupPairs.keyGroup and book4_Pheonix.b4_sim=groupPairs.simnumber and draw = 'Part 4'
	left join book4_ties as keyTies on book4_Pheonix.b4_sim=keyTies.simnumber and book4_Pheonix.b4_teamGroup = keyTies.teamgroup
	left join book4_ties as oppoTies on book4_Pheonix.b4_sim=oppoTies.simnumber and groupPairs.oppogroup = oppoTies.teamgroup
)

select b1_sim,b1_conf,b1_group1,b1_group2,b1_totalDrawGames,

		b4_sim, 
		b4_conference, 
		b4_group, 
		b4_oppogroup, 
		b4_PheonixTies, 
		totalties
from book4 as d
left join book1 on d.b4_sim = book1.b1_sim
-- where	1=1
-- 	
	
	
-- SELECT simnumber, conference, division, teamgroup, team, prewu1rank, postwu1rank, prewu2rank, postwu2rank, prewu3rank, postwu3rank, prewu4rank, postwu4rank
-- 	FROM seasons.rankchanges
-- 	where simnumber = 2 and teamgroup = 'Rush Group'
	
	
;