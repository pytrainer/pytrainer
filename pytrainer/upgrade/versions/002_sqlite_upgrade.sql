-- laps added in version 1.7.2
create table laps (
	id_lap integer primary key autoincrement,
	record integer,
	elapsed_time varchar(20),
	distance float,
	start_lat float,
	start_lon float,
	end_lat float,
	end_lon float,
	calories integer
);
