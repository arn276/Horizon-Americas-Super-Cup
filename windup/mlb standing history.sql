with
 results as (SELECT extract(year from game_date) as season,game_date,
	road_tm as tm, 
	case when roadscore > homescore then 1 else 0 end as wins,
	case when roadscore < homescore then 1 else 0 end as losses,
	case when roadscore = homescore then 1 else 0 end as tie
	FROM gamelogs.games
	where extract(year from game_date) = 1969
		-- and game_date = '1969-04-15'
	
	union all

	select extract(year from game_date) as season,game_date,
	home_tm as tm, 
	case when roadscore < homescore then 1 else 0 end as wins,
	case when roadscore > homescore then 1 else 0 end as losses,
	case when roadscore = homescore then 1 else 0 end as tie
	
	-- game_date, number_of_games, day_of_week, road_tm, road_lg, road_tm_game_num, home_tm, home_lg, home_tm_game_num, roadscore, homescore, length_of_game_outs, day_or_night, completion_information, forfeit, protest, parkid, attendance, time_of_game_min, road_linescore, home_linescore, road_ab, road_h, road_double, road_triple, road_hr, road_rbi, road_sachit, road_sacfly, road_hbp, road_bb, road_ibb, road_strikeout, road_sb, road_cs, road_gdb, road_catcher_int, road_lob, road_pitcher_used, road_ind_er, road_tm_er, road_wp, road_balk, road_putout, road_assists, road_errors, road_pb, road_double_play, road_triple_play, home_ab, home_h, home_double, home_triple, home_hr, home_rbi, home_sachit, home_sacfly, home_hbp, home_bb, home_ibb, home_strikeout, home_sb, home_cs, home_gdb, home_catcher_int, home_lob, home_pitcher_used, home_ind_er, home_tm_er, home_wp, home_balk, home_putout, home_assists, home_errors, home_pb, home_double_play, home_triple_play, ump_homeid, ump_homename, ump_1bid, ump_1bname, ump_2bid, ump_2bname, ump_3bid, ump_3bname, ump_lfid, ump_lfname, ump_rfid, ump_rfname, road_mgrid, road_mgrname, home_mgrid, home_mgrname, winning_ptcher_id, winning_ptcher_name, losing_ptcher_id, losing_ptcher_name, saving_ptcher_id, saving_ptcher_name, game_winning_rbi_id, game_winning_rbi_name, road_sp_id, road_sp_name, home_sp_id, home_sp_name, road_bat1_id, road_bat1_name, road_bat1_pos, road_bat2_id, road_bat2_name, road_bat2_pos, road_bat3_id, road_bat3_name, road_bat3_pos, road_bat4_id, road_bat4_name, road_bat4_pos, road_bat5_id, road_bat5_name, road_bat5_pos, road_bat6_id, road_bat6_name, road_bat6_pos, road_bat7_id, road_bat7_name, road_bat7_pos, road_bat8_id, road_bat8_name, road_bat8_pos, road_bat9_id, road_bat9_name, road_bat9_pos, home_bat1_id, home_bat1_name, home_bat1_pos, home_bat2_id, home_bat2_name, home_bat2_pos, home_bat3_id, home_bat3_name, home_bat3_pos, home_bat4_id, home_bat4_name, home_bat4_pos, home_bat5_id, home_bat5_name, home_bat5_pos, home_bat6_id, home_bat6_name, home_bat6_pos, home_bat7_id, home_bat7_name, home_bat7_pos, home_bat8_id, home_bat8_name, home_bat8_pos, home_bat9_id, home_bat9_name, home_bat9_pos, additional_info, acquisition_info
	FROM gamelogs.games
	where extract(year from game_date) = 1969
		-- and game_date = '1969-04-15'
)

select season, tm, sum(wins), sum(losses), sum(tie)
from results
-- where game_date = '1969-04-15'
group by season, tm
