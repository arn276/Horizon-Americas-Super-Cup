with drawImpact as (
	SELECT distinct simnumber, conference, division, teamgroup, team, 
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
		and home.teamgroup != away.teamgroup
),

standingSummary as(
	select distinct simnumber, conference, division, teamgroup, team,
	seasonpart,
	sum(case when timing = 'pre Wind-up' then winningpct else null end)over(partition by simnumber, teamgroup, team, seasonpart) as winningpct,
	sum(case when timing = 'pre Wind-up' then wins else null end)over(partition by simnumber, teamgroup, team, seasonpart)   as preDraw_wins,
	sum(case when timing = 'post Wind-up' then wins else null end)over(partition by simnumber, teamgroup, team, seasonpart)   as postDraw_wins,
	sum(case when timing = 'pre Wind-up' then tiestofinish else null end)over(partition by simnumber, teamgroup, team, seasonpart) as drawTies
	from seasons.standings
),


s1_staleGrps as(
	select distinct d.simnumber, d.conference, d.division, d.teamgroup, d.team,
		winningpct,preDraw_wins,postDraw_wins,
		-- sum(case when timing = 'pre Wind-up' then winningpct else null end)over(partition by d.simnumber, d.teamgroup, d.team) as winningpct,
		-- sum(case when timing = 'pre Wind-up' then wins else null end)over(partition by d.simnumber, d.teamgroup, d.team)   as preDraw_wins,
		-- sum(case when timing = 'post Wind-up' then wins else null end)over(partition by d.simnumber, d.teamgroup, d.team)   as postDraw_wins,
		-- prewu1rank, postwu1rank,tiestofinish,
		sum(NoChange)over(partition by d.simnumber, d.teamgroup) as stale,
		sum(drawTies)over(partition by d.simnumber, d.teamgroup) as totalties
		-- sum(case when timing = 'post Wind-up' then NoChange else null end)over(partition by d.simnumber, d.teamgroup) as stale,
		-- sum(case when timing = 'pre Wind-up' then tiestofinish else null end)over(partition by d.simnumber, d.teamgroup) as totalties
	from drawImpact as d
	-- left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 1' --and timing = 'pre Wind-up'
	left join standingSummary as s on d.simnumber = s.simnumber and d.team = s.team and s.seasonpart = 'Part 1'
	
),

s1_staleScores as (
	select simnumber, conference, division, teamgroup,
		-- team, 
		preDraw_wins - lead(preDraw_wins,1)over(partition by simnumber, conference, division, teamgroup order by teamgroup,winningpct desc) as preStaleScore,
		postDraw_wins - lead(postDraw_wins,1)over(partition by simnumber, conference, division, teamgroup order by teamgroup,winningpct desc) as postStaleScore,
		totalties
	from s1_staleGrps
	where stale = 4 

),

s1_grpLevel as (
	select s.simnumber, s.conference, s.division, s.teamgroup,oppoGroup, 
		(sum(preStaleScore)+avg(totalties)) - (sum(postStaleScore)+avg(totalties)) levelOfStale,
		totalties
	from  s1_staleScores as s
	left join groupPairs as gP on s.simnumber=gP.simnumber and s.teamgroup = gP.keyGroup and gP.draw = 'Part 1'
	group by s.simnumber, s.conference, s.division, s.teamgroup, oppoGroup, totalties
),

s1 as(
	select distinct g1.simnumber as s1_sim, g1.conference as s1_conf, 
		case
		when g1.teamgroup > g1.oppoGroup then g1.oppoGroup
		else g1.teamgroup
		end as s1_group1, 
		
		case
		when g1.teamgroup < g1.oppoGroup then g1.oppoGroup
		else g1.teamgroup
		end as s1_group2, 
		g1.levelOfStale+g2.levelOfStale as s1_levelOfStale,
		(g1.totalties+g2.totalties)/2 as s1_totalDrawGames
	from s1_grpLevel as g1
	inner join s1_grpLevel as g2 on g1.oppoGroup = g2.teamgroup and g1.simnumber = g2.simnumber
),

s3_Philly as (
	select d.simnumber as s3_sim, 
		d.conference as s3_conference, 
		d.teamgroup as s3_teamGroup, 
		d.team as s3_team, 
		prewu4rank as s3_preDraw, 
		postwu4rank as s3_postDraw, 
		tiestofinish as s3_teamTies,
		max(tiestofinish)over(partition by d.simnumber, d.conference) as s3_mostTies
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 3' and timing = 'pre Wind-up'
	where d.conference = 'Founders'  --d.team ='Philadelphia' 
		and s.seasonpart = 'Part 3' and s.timing = 'pre Wind-up'
		-- and tiestofinish>=4
),

s3_ties as(
	select distinct d.simnumber, d.conference, d.division, d.teamgroup,
		sum(tiestofinish)over(partition by d.simnumber, d.teamgroup) as totalties
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 3' and timing = 'pre Wind-up'
),

s3 as (
	select distinct s3_sim, s3_conference, s3_team, keyGroup as s3_group, oppogroup as s3_oppogroup, 
		-- s3_PhillyTies, 
		s3_mostTies, (keyTies.totalties+oppoTies.totalties)/2 as s3_totalties
	from s3_Philly
	left join groupPairs on s3_Philly.s3_teamGroup = groupPairs.keyGroup and s3_Philly.s3_sim=groupPairs.simnumber and draw = 'Part 3'
	left join s3_ties as keyTies on s3_Philly.s3_sim=keyTies.simnumber and s3_Philly.s3_teamGroup = keyTies.teamgroup
	left join s3_ties as oppoTies on s3_Philly.s3_sim=oppoTies.simnumber and groupPairs.oppogroup = oppoTies.teamgroup
	where s3_mostTies = s3_teamTies
),

s4_Pheonix as (
	select d.simnumber as s4_sim, 
		d.conference as s4_conference, 
		d.teamgroup as s4_teamGroup, 
		d.team as s4_team, 
		prewu4rank as s4_preDraw, 
		postwu4rank as s4_postDraw, 
		tiestofinish as s4_PheonixTies
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 4' and timing = 'pre Wind-up'
	where 1=1 
		-- and d.teamgroup ='Rush Group' --d.team ='Pheonix'
		and d.conference = 'Visionaries'
		and prewu4rank = 1 and postwu4rank != 1
		and s.seasonpart = 'Part 4' and s.timing = 'pre Wind-up'
		and tiestofinish>=4
),

s4_ties as(
	select distinct d.simnumber, d.conference, d.division, d.teamgroup,
		sum(tiestofinish)over(partition by d.simnumber, d.teamgroup) as totalties
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 4' and timing = 'pre Wind-up'
),

s4_winDiff as (
	select distinct s4_sim, s4_team,s4_PheonixTies,--t1.preDraw_wins, t1.postDraw_wins,t1.drawTies,
		st.team as passingteam,--t2.preDraw_wins, t2.postDraw_wins,t2.drawTies,
		max(t1.preDraw_wins)over(partition by s4_sim, s4_team) - avg(t2.preDraw_wins)over(partition by s4_sim) pre_winsDistance,
		max(t1.postDraw_wins)over(partition by s4_sim, s4_team) - avg(t2.postDraw_wins)over(partition by s4_sim) post_winsDistance
	from s4_Pheonix
	left join groupPairs on s4_Pheonix.s4_teamGroup = groupPairs.keyGroup and s4_Pheonix.s4_sim=groupPairs.simnumber and draw = 'Part 4'
	left join seasons.standings as st on s4_Pheonix.s4_sim = st.simnumber and groupPairs.keyGroup = st.teamgroup and st.timing = 'post Wind-up' and st.seasonpart = 'Part 4' and st.standingrank = 1
	left join standingSummary as t1 on s4_Pheonix.s4_sim = t1.simnumber and s4_Pheonix.s4_team = t1.team and  t1.seasonpart = 'Part 4'
	left join standingSummary as t2 on s4_Pheonix.s4_sim = t2.simnumber and st.team = t2.team and  t2.seasonpart = 'Part 4'
),

s4_score as (
	select distinct s4_sim, s4_team, pre_winsDistance-post_winsDistance + count(gamedate)over(partition by s4_sim, s4_team)/cast(s4_PheonixTies as float) as compelScore
	from s4_winDiff
	left join seasons.results as r on s4_winDiff.s4_sim = r.simnumber and gamedate >'8/15/2010' and wrapupresult != '' and hometeam in (s4_team, passingteam) and awayteam in (s4_team, passingteam)
),

s4 as (
	select distinct s.s4_sim, s4_conference, keyGroup as s4_group, s.s4_team, --st.team as passingteam,
			oppogroup as s4_oppogroup, compelScore, s4_PheonixTies, (keyTies.totalties+oppoTies.totalties)/2 as s4_totalties
	from s4_Pheonix as s
	left join groupPairs on s.s4_teamGroup = groupPairs.keyGroup and s.s4_sim=groupPairs.simnumber and draw = 'Part 4'
	left join s4_ties as keyTies on s.s4_sim=keyTies.simnumber and s.s4_teamGroup = keyTies.teamgroup
	left join s4_ties as oppoTies on s.s4_sim=oppoTies.simnumber and groupPairs.oppogroup = oppoTies.teamgroup
	left join s4_score as sc on s.s4_sim = sc.s4_sim and s.s4_team = sc.s4_team
),

s2_ties as(
	select distinct d.simnumber, d.conference, d.division, d.teamgroup,
		sum(tiestofinish)over(partition by d.simnumber, d.teamgroup) as totalties
	from drawImpact as d
	left join seasons.standings as s on d.simnumber=s.simnumber and d.team = s.team and s.seasonpart = 'Part 2' and timing = 'pre Wind-up'
	-- where d.simnumber in (330,220)
),

s2 as (
	select s.simnumber, s.conference, s.division, s.teamgroup,s.totalties, oppoTies.teamgroup, oppoTies.totalties
	from s2_ties as s
	left join groupPairs on s.teamgroup = groupPairs.keyGroup and s.simnumber=groupPairs.simnumber and draw = 'Part 2'
	left join s2_ties as oppoTies on s.simnumber=oppoTies.simnumber and groupPairs.oppogroup = oppoTies.teamgroup
)

select s4_sim,s1_conf,s1_group1,s1_group2,s1_totalDrawGames,s1_levelOfStale,
		s3_conference, s3_group, s3_oppogroup, s3_team,--s3_PhillyTies, 
			s3_mostTies, s3_totalties,
		s4_conference, s4_group, s4_team, s4_oppogroup, s4_PheonixTies, s4_totalties, compelScore
from s4 as d
left join s1 on d.s4_sim = s1.s1_sim
left join s3 on d.s4_sim = s3.s3_sim
where s1_levelOfStale >=0
	and s3_conference is not null 
order by compelScore desc 

-- select *
-- from s1_stale
-- where simnumber = 51 and teamgroup = 'Ridge Group'

-- select *
-- from s3_Philly
-- where b3_sim = 164









