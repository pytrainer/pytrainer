-- laps added in version 1.7.1
create table laps (
	id_lap integer primary key auto_increment,
	record integer,
	elapsed_time varchar(20),
	distance float,
	start_lat float,
	start_lon float,
	end_lat float,
	end_lon float,
	calories integer
);
