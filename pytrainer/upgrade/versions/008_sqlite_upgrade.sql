-- equipment management added in version 1.8.0

create table equipment (
	id integer primary key autoincrement ,
	description varchar(200),
	active boolean,
	life_expectancy int,
	prior_usage int,
	notes text
);

create table record_equipment (
	id integer primary key autoincrement,
	record_id int,
	equipment_id int
);
