"""Create media.example.db with a small sample of titles.

Note: could also use SQLite's ATTACH DATABASE to query across
both files directly instead of fetch-then-insert.
"""

import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()
cur.execute("""
    SELECT * FROM media                  
    WHERE title IN (
    'Armageddon',
    'Alita: Battle Angel',
    'Avengers: Age of Ultron',
    'Batman Returns',
    'Beauty and the Beast',
    'Blade Runner',
    'Black Panther',
    'Cast Away',
    'Captain America: The Winter Soldier',
    'Cars 2',
    'Blue Bloods',
    'Better Call Saul',
    'CSI: Crime Scene Investigation',
    'Casino Royale',
    'Chicago Med'
    )
""")

sample_data = cur.fetchall()
print(sample_data)

conn.close()

new_db = sqlite3.connect('../data/media.example.db')
new_cur = new_db.cursor()

new_cur.execute("""
CREATE TABLE media (
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

new_cur.executemany("INSERT INTO media VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sample_data)

new_db.commit()

check_table = new_cur.execute("SELECT * FROM media").fetchall()
print(check_table)

new_db.close()
print('Connection closed.')