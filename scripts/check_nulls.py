import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()
result = cur.execute("""
    SELECT
        COUNT(*) - COUNT(imdb_id) AS imdb_id_nulls,
        COUNT(*) - COUNT(title) AS title_nulls,
        COUNT(*) - COUNT(year) AS year_nulls,
        COUNT(*) - COUNT(genres) AS genres_nulls,
        COUNT(*) - COUNT(runtime_mins) AS runtime_mins_nulls,
        COUNT(*) - COUNT(studio) AS studio_nulls,
        COUNT(*) - COUNT(tagline) AS tagline_nulls,
        COUNT(*) - COUNT(description) AS description_nulls,
        COUNT(*) - COUNT(tmdb_id) AS tmdb_id_nulls,
        COUNT(*) - COUNT(source) AS source_nulls,
        COUNT(*) - COUNT(type) AS type_nulls,
        COUNT(*) - COUNT(number_of_seasons) AS number_of_seasons_nulls,
        COUNT(*) - COUNT(number_of_episodes) AS number_of_episodes_nulls,
        COUNT(*) - COUNT(original_title) AS original_title_nulls,
        COUNT(*) - COUNT(imdb_rating) AS imdb_rating_nulls,
        COUNT(*) - COUNT(release_date) AS release_date_nulls,
        COUNT(*) - COUNT(directors) AS directors_nulls,
        COUNT(*) - COUNT(poster_path) AS poster_path_nulls,
        COUNT(*) - COUNT("cast") AS cast_nulls
    FROM media
""").fetchall()
print(result)
conn.close()