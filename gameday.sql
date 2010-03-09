DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
        game_id varchar(30) not null primary key,
	game_type char(1) not null,
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
	away_fname varchar(50) default null,
	away_sname varchar(50) default null,
	away_wins int default null,
	away_loss int default null,
	status_ind char(1) default null,
        date date default null
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `atbat`;
CREATE TABLE `atbat` (
	/* custom fields */
	game_id varchar(30) not null,
	half varchar(10) default null,
	inning int default null,
	/* gameday fields */
	num int,
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
	away_team_runs int default 0,
	primary key (game_id, num)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `pitch`;
CREATE TABLE `pitch` (
	/* custom fields */
	game_id varchar(30) not null,
	num int,
	pitcher int,
	b tinyint(1) default 0,
	s tinyint(1) default 0,
	/* gameday fields */
	des varchar(100),
	id int default 0,
	type varchar(3) not null,
	x float default 0,
	y float default 0,
	on_1b int default null,
	on_2b int default null,
	on_3b int default null,
	sv_id varchar(20) default null,
	start_speed float default 0,
	end_speed float default 0,
	sz_top float default 0,
	sz_bot float default 0,
	pfx_x float default 0,
	pfx_z float default 0,
	px float default 0,
	pz float default 0,
	x0 float default 0,
	y0 float default 0,
	z0 float default 0,
	vx0 float default 0,
	vy0 float default 0,
	vz0 float default 0,
	ax float default 0,
	ay float default 0,
	az float default 0,
	break_y float default 0,
	break_angle float default 0,
	break_length float default 0,
	pitch_type char(2) default null,
	type_confidence float default 0,
	spin_dir float default 0,
	spin_rate float default 0,
	zone tinyint default 0,
	primary key(game_id, num, id)
) Engine=InnoDB;

DROP TABLE IF EXISTS `hitchart`;
CREATE TABLE `hitchart` (
        game_id varchar(30) not null primary key,
	des varchar(25) default null,
	x float default null,
	y float default null,
	batter int default null,
	pitcher int default null,
	type char(1) default null,
	team enum('H', 'A'),
	inning tinyint default null
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
	team varchar(3) default null,
	id int primary key,
	pos varchar(3) default null,
	type enum('pitcher', 'batter'),
	first_name varchar(30) default null,
	last_name varchar(30) default null,
	jersey_number varchar(2) default null,
	height varchar(5) default null,
	weight int default null,
	bats varchar(3) default null,/* enum('L', 'R', 'S'),*/
	throws varchar(3) default null,/* enum('L', 'R'),*/
	dob varchar(20) default null
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `last`;
CREATE TABLE `last` (
	type varchar(5),
	year int,
	month int,
	day int
) ENGINE=InnoDB;
