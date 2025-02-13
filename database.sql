create table urls
(
	id serial primary key,
	name varchar(255),
	created_at default current_timestamp
);

create table url_checks
(
	id serial primary key,
	url_id int not null,
	status_code int,
	h1 varchar,
	title varchar,
	description varchar,
	created_at timestamp default current_timestamp,
	foreign key(url_id) references urls(id)
);