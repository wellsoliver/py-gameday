DROP TABLE IF EXISTS `game`;
CREATE TABLE `game` (
        game_id varchar(30) default null,
		game_pk int default null,
		home_sport_code varchar(10) default null,
		away_team_code varchar(5) default null,
		home_team_code varchar(5) default null,
        home varchar(30) default null,
        away varchar(30) default null,
        date date default null
) ENGINE=InnoDB;
