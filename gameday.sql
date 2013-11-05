DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
	game_id varchar(30) not null primary key,
	game_type char(1) not null,
	local_game_time varchar(10) default null,
	game_pk int default null,
	game_time_et varchar(10) default null,
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
	`date` date default null,
	day varchar(3) default null,
	stadium_id int default null,
	stadium_name varchar(30) default null,
	stadium_location varchar(30) default null
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `atbat`;
CREATE TABLE `atbat` (
	/* custom fields */
	game_id varchar(30) not null,
	half varchar(10) default null,
	inning int default null,
	/* gameday fields */
	num int not null,
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
	des_es varchar(500) default null,
	event varchar(200) default null,
	event2 varchar(200) default null,
	event3 varchar(200) default null,
	home_team_runs int default null,
	away_team_runs int default null,
	start_tfs int default null,
	start_tfs_zulu varchar(25) default null,
	primary key (game_id, num)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `pitch`;
CREATE TABLE `pitch` (
	/* custom fields */
	game_id varchar(30) not null,
	num int default null,
	pitcher int default null,
	batter int default null,
	b tinyint default null,
	s tinyint default null,
	/* gameday fields */
	des varchar(100) default null,
	id int default null,
	type varchar(3) not null,
	x decimal(7,3) default null,
	y decimal(7,3) default null,
	on_1b int default null,
	on_2b int default null,
	on_3b int default null,
	sv_id varchar(20) default null,
	start_speed decimal(7,3) default null,
	end_speed decimal(7,3) default null,
	sz_top decimal(7,3) default null,
	sz_bot decimal(7,3) default null,
	pfx_x decimal(7,3) default null,
	pfx_z decimal(7,3) default null,
	px decimal(7,3) default null,
	pz decimal(7,3) default null,
	x0 decimal(7,3) default null,
	y0 decimal(7,3) default null,
	z0 decimal(7,3) default null,
	vx0 decimal(7,3) default null,
	vy0 decimal(7,3) default null,
	vz0 decimal(7,3) default null,
	ax decimal(7,3) default null,
	ay decimal(7,3) default null,
	az decimal(7,3) default null,
	break_y decimal(7,3) default null,
	break_angle decimal(7,3) default null,
	break_length decimal(7,3) default null,
	pitch_type char(2) default null,
	type_confidence decimal(7,3) default null,
	spin_dir decimal(7,3) default null,
	spin_rate decimal(7,3) default null,
	zone tinyint default null,
	primary key(game_id, num, id)
) Engine=InnoDB;

DROP TABLE IF EXISTS `hitchart`;
CREATE TABLE `hitchart` (
	hit_id int unsigned not null auto_increment primary key,
	game_id varchar(30) not null,
	des varchar(25) default null,
	x decimal(7,3) default null,
	y decimal(7,3) default null,
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
	current_position varchar(3) default null,
	last_name varchar(30) default null,
	jersey_number varchar(2) default null,
	height varchar(5) default null,
	weight int default null,
	bats varchar(3) default null,
	throws varchar(3) default null,
	dob varchar(20) default null
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `last`;
CREATE TABLE `last` (
	type varchar(5),
	year int,
	month int,
	day int
) ENGINE=InnoDB;
