-- record date_time data type changed in version 1.8.0
alter table records
	modify date_time_local varchar(40),
	modify date_time_utc varchar(40);