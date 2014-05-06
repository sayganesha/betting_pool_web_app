drop table if exists users;
create table users (
	user_id integer primary key autoincrement,
	name text not null
);

drop table if exists bet_info;
create table bet_info (
	bet_id integer primary key autoincrement,
	name text not null,
	desc text not null,
	pic  text
);

drop table if exists bet_options;
create table bet_options (
	bet_opt_id integer primary key autoincrement,
	bet_id integer not null,
	name text not null
);

drop table if exists user_bets;
create table user_bets (
	user_id integer not null,
	bet_opt_id integer not null,
	amount integer not null
);
