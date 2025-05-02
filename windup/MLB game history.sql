with games as(
	SELECT  extract(year from game_date) as season, game_date, number_of_games, 
		road_tm,road_lg,  home_tm,home_lg,
		roadscore, homescore, length_of_game_outs, time_of_game_min,
		forfeit, parkid, attendance, road_pitcher_used, home_pitcher_used
	FROM gamelogs.games as g
	order by extract(year from game_date)
)


select distinct season, game_date, number_of_games, 
	road_tm, t_r.city, t_r.nickname, road_lg, 
	home_tm, t_h.city, t_h.nickname, home_lg,
	roadscore, homescore, length_of_game_outs, time_of_game_min,
	forfeit, parkid, attendance, road_pitcher_used, home_pitcher_used
from games
left join rosters.teams as t_r on games.road_tm = t_r.abrv and games.season = t_r.year
left join rosters.teams as t_h on games.home_tm = t_h.abrv and games.season = t_h.year

order by season desc, game_date
