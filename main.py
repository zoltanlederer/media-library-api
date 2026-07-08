from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI()  # The main application instance — every route gets attached to this


@app.get('/media')
def get_media(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    actor: Optional[str] = None,
    media_type: Optional[str] = None,
    ):
    """Return all media items from the database as validated MediaItem objects."""

    # Open a fresh connection for this request (not shared/reused between requests)
    conn = sqlite3.connect('./data/media.db')

    # row_factory makes each row behave like a dict (access by column name),
    # instead of a plain unnamed tuple
    conn.row_factory = sqlite3.Row

    condition = []
    values = []

    if title is not None:
        condition.append('title LIKE ?')
        values.append(f'%{title}%')
    if genre is not None:
        condition.append('genres LIKE ?')
        values.append(f'%{genre}%')
    if year is not None:
        condition.append('year = ?')
        values.append(year)
    if actor is not None:
        condition.append('"cast" LIKE ?')
        values.append(f'%{actor}%')
    if media_type is not None:
        condition.append('"type" = ?')
        values.append(media_type)

    cur = conn.cursor()
    if condition:
        final_condition =  ' AND '.join(condition)
        cur.execute(f"SELECT * FROM media WHERE {final_condition}", values)
    else: 
        cur.execute('SELECT * FROM media')
    data = cur.fetchall()

    # Convert each raw row into a validated MediaItem
    # (checks types, and shapes the JSON response with named fields)
    all_data = []
    for row in data:
        all_data.append(MediaItem(**dict(row)))

    conn.close()  # release the connection now that we're done with it

    return all_data


class MediaItem(BaseModel):
    """Defines the shape and validation rules for one row in the media table.

    Only id, title, source, and type are guaranteed non-null across the
    real dataset (confirmed via scripts/check_nulls.py) — everything else
    uses Optional since real rows are often missing these values.
    """
    id: int
    imdb_id: Optional[str] = None
    title: str
    year: Optional[int] = None
    genres: Optional[str] = None
    runtime_mins: Optional[int] = None
    studio: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    tmdb_id: Optional[int] = None
    source: str
    type: str
    number_of_seasons: Optional[int] = None
    number_of_episodes: Optional[int] = None
    original_title: Optional[str] = None
    imdb_rating: Optional[float] = None
    release_date: Optional[str] = None
    directors: Optional[str] = None
    poster_path: Optional[str] = None
    cast: Optional[str] = None