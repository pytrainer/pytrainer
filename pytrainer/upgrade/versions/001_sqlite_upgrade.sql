-- initial schema as of version 1.7.1

create table sports  (
	id_sports integer primary key autoincrement,
	name varchar(100),
	weight float,
	met float
);

create table records  (
	id_record integer primary key autoincrement,
	date date,
	sport integer,
	distance float,
	time varchar(200),
	beats float,
	average float,
	calories int,
	comments text,
	gpslog varchar(200),
	title varchar(200),
	upositive float,
	unegative float,
	maxspeed float,
	maxpace float,
	pace float,
	maxbeats float,
	date_time_local varchar(20),
	date_time_utc varchar(20)
);

create table waypoints  (
	id_waypoint integer primary key autoincrement,
	lat float,
	lon float,
	ele float,
	comment varchar(240),
	time date,
	name varchar(200),
	sym varchar(200)
);
