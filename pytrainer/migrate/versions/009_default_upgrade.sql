-- lap info added in version 1.9.0
alter table laps add intensity varchar(7);
alter table laps add laptrigger(9);
alter table laps add max_speed float;
alter table laps add avg_hr int;
alter table laps add max_hr int;
alter table laps add comments text;