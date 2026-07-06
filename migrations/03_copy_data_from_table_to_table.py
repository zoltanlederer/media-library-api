import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()

cur.execute("""
INSERT INTO media_new (
    imdb_id,
    title,
    year,
    genres,
    runtime_mins,
    studio,
    tagline,
    description,
    tmdb_id,
    source,
    type,
    number_of_seasons,
    number_of_episodes,
    original_title,
    imdb_rating,
    release_date,
    directors,
    poster_path,
    "cast")
SELECT
    imdb_id,
    title,
    year,
    genres,
    runtime_mins,
    studio,
    tagline,
    description,
    tmdb_id,
    source,
    type,
    number_of_seasons,
    number_of_episodes,
    original_title,
    imdb_rating,
    release_date,
    directors,
    poster_path,
    "cast"
FROM media
""")

conn.commit()
conn.close()
print('Connection closed.')
