import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, request
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Literal
from datetime import date


load_dotenv()


app = Flask(__name__)
app.json.ensure_ascii = False

connection = psycopg2.connect(
    host=(
        os.getenv("POSTGRES_HOST")
        if os.getenv("DEBUG_MODE") == "false"
        else "localhost"
    ),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    cursor_factory=RealDictCursor,
)
connection.autocommit = True




@app.get("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.get("/videos")
def get_videos():
    query = """
with video_with_user as
(select 
	v.id,
	v.name_video,
	v.date_publication,
	v.during,
	coalesce (json_agg(json_build_object(
	'id', u.id, 'user_name', u.user_name, 'date_registrated', u.date_registrated
	)) filter (where u.id is not null), '[]') as users from video_data.videos v
	left join video_data.user_video uv on uv.video_id = v.id
	left join video_data.users u on uv.user_id = u.id
	group by v.id),

videos_with_movie as 
(select 
	v.id,
	coalesce (json_agg(json_build_object(
	'id', c.id, 'comment_text', c.comment_text, 'date_publication', c.date_publication, 'count_likes', c.count_likes 
	)) filter (where c.id is not null), '[]') as "comment" from video_data.videos v 
	left join video_data."comments" c on c.id = v.comments_id
	group by v.id)
	

select vwu.id, name_video, date_publication, during, users, "comment" from video_with_user vwu
left join videos_with_movie vwm on vwm.id = vwu.id 
"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return result


@app.post("/videos")
def create_video():
    body = request.json

    name_video = body["name_video"]
    date_publication = body["date_publication"]
    during = body["during"]

    query = SQL(
        """
insert into video_data.videos(name_video, date_publication, during)
values ({name_video}, {date_publication}, {during})
returning id
"""
    ).format(
        name_video=Literal(name_video),
        date_publication=Literal(date_publication),
        during=Literal(during),
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()

    return result


@app.put("/videos")
def update_video():
    body = request.json

    id = body["id"]
    name_video = body["name_video"]
    date_publication = body["date_publication"]
    during = body["during"]

    query = SQL(
        """
update video_data.videos
set 
  name_video = {name_video}, 
  date_publication = {date_publication},
  during = {during}
where id = {id}
returning id
"""
    ).format(
        name_video=Literal(name_video),
        date_publication=Literal(date_publication),
        during=Literal(during),
        id=Literal(id),
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    if len(result) == 0:
        return "", 404

    return "", 204


@app.delete("/videos")
def delete_video():
    body = request.json

    id = body["id"]

    deleteActorLinks = SQL(
        "delete from  video_data.user_video where video_id = {id}"
    ).format(id=Literal(id))
    deleteActor = SQL(
        "delete from video_data.videos where id = {id} returning id"
    ).format(id=Literal(id))

    with connection.cursor() as cursor:
        cursor.execute(deleteActorLinks)
        cursor.execute(deleteActor)
        result = cursor.fetchall()

    if len(result) == 0:
        return "", 404

    return "", 204


if __name__ == "__main__":
    app.run(port=os.getenv("FLASK_PORT"))
