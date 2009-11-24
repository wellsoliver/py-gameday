DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
        game_id varchar(30) not null primary key,
		game_pk int default null,

		home_sport_code varchar(10) default null,
		home_id int default null,
		home_team_code varchar(3) default null,
		home_fname varchar(30) default null,
		home_sname varchar(30) default null,
		home_wins int default null,
		home_loss int default null,

		away_id int default null,
		away_team_code varchar(3) default null,
		away_fname varchar(30) default null,
		away_sname varchar(30) default null,
		away_wins int default null,
		away_loss int default null,
		status_ind char(1) default null,
        date date default null
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `atbat`;
CREATE TABLE `atbat` (
	game_id varchar(30) not null,
	num int,
	half varchar(10) default null,
	b int default null,
	s int default null,
	o int default null,
	score char(1) default null,
	batter int default null,
	stand char(1) default null,
	b_height varchar(5) default null,
	pitcher int default null,
	p_throws char(1) default null,
	des varchar(500) default null,
	event varchar(200) default null,
	home_team_runs int default 0,
	away_team_runs int default 0
) ENGINE=InnoDB;