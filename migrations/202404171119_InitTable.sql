-- migrate:up

CREATE SCHEMA video_data; 
drop table if exists video_data.videos, video_data.users, video_data."comments" cascade;
CREATE extension if not exists "uuid-ossp";


create table if not exists video_data."comments" (
	id uuid primary key default uuid_generate_v4(),
	comment_text text,
	date_publication date,
	count_likes int
);

CREATE TABLE if not exists video_data.videos (
	id uuid primary key default uuid_generate_v4(),
	name_video text,
	date_publication date,
	during int,
	comments_id uuid references video_data."comments"
);

create table if not exists video_data.users (
	id uuid primary key default uuid_generate_v4(),
	user_name text,
	date_registrated date
);




create table if not exists video_data.user_video(
	user_id uuid references video_data.users,
	video_id uuid references video_data.videos,
	primary key(user_id, video_id)
);

-- migrate:down