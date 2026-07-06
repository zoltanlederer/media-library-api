"""Add a proper id primary key column to the table."""

import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()

cur.execute("""
CREATE TABLE media_new (
    id INTEGER PRIMARY KEY,
    imdb_id TEXT,
    title TEXT,
    year INTEGER,
    genres TEXT,
    runtime_mins INTEGER,
    studio TEXT,
    tagline TEXT,
    description TEXT,
    tmdb_id INTEGER,
    source TEXT,
    type TEXT,
    number_of_seasons INTEGER,
    number_of_episodes INTEGER,
    original_title TEXT,
    imdb_rating REAL,
    release_date TEXT,
    directors TEXT,
    poster_path TEXT,
    cast TEXT
)
""")

conn.commit()
conn.close()
print("media_new table created.")