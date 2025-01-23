create table urls
(
	id serial primary key,
	name varchar,
	created_at default current_timestamp
);
