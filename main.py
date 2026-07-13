from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
import sqlite3

# Load variables from .env into the environment, then read the API key out.
# The real key lives only in .env (gitignored) — never hardcoded here.
load_dotenv()
API_KEY = os.getenv("API_KEY")

# No default — DB_PATH must be set explicitly in .env (see README).
# Points at media.db locally, media.example.db when deployed.
DB_PATH = os.getenv("DB_PATH")

app = FastAPI()  # The main application instance — every route gets attached to this


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


class MediaItemUpdate(BaseModel):
    """Same fields as MediaItem, but every field is optional and defaults to
    None — used as the PATCH request body, so a client can send just the
    field(s) they want to change, without resending the whole item.
    """
    imdb_id: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    genres: Optional[str] = None
    runtime_mins: Optional[int] = None
    studio: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    tmdb_id: Optional[int] = None
    source: Optional[str] = None
    type: Optional[str] = None
    number_of_seasons: Optional[int] = None
    number_of_episodes: Optional[int] = None
    original_title: Optional[str] = None
    imdb_rating: Optional[float] = None
    release_date: Optional[str] = None
    directors: Optional[str] = None
    poster_path: Optional[str] = None
    cast: Optional[str] = None


class MediaItemNew(BaseModel):
    """Request body for creating a new media item. id is deliberately not
    included — SQLite auto-assigns it, the client never provides one.
    title, source, and type are required; everything else is optional.
    """
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


def verify_api_key(x_api_key: str = Header(...)):
    """Dependency that guards write endpoints (POST/PATCH/DELETE).

    FastAPI runs this before the route's own code. Header(...) reads the
    X-API-Key header (FastAPI converts the hyphenated header name to this
    underscored parameter name automatically). Raises 401 if it's missing
    or wrong; otherwise the request is allowed through. GET endpoints don't
    use this — reads stay public, only writes require the key.
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')


@app.get('/media')
def get_media(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    actor: Optional[str] = None,
    media_type: Optional[str] = None,
    ):
    """Return all media items from the database as validated MediaItem objects.

    All filters are optional and combined with AND — e.g. title + year
    together narrow the results, rather than broadening them. No filters
    given returns every row.
    """

    # Open a fresh connection for this request (not shared/reused between requests)
    conn = sqlite3.connect(DB_PATH)

    # row_factory makes each row behave like a dict (access by column name),
    # instead of a plain unnamed tuple
    conn.row_factory = sqlite3.Row

    # Build the WHERE clause dynamically — only include conditions for
    # filters that were actually provided
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
        # cast is a reserved SQL keyword — must be quoted to use as a column name
        condition.append('"cast" LIKE ?')
        values.append(f'%{actor}%')
    if media_type is not None:
        condition.append('"type" = ?')
        values.append(media_type)

    cur = conn.cursor()
    if condition:
        final_condition = ' AND '.join(condition)
        cur.execute(f"SELECT * FROM media WHERE {final_condition}", values)
    else:
        # No filters provided — return everything
        cur.execute('SELECT * FROM media')
    data = cur.fetchall()

    # Convert each raw row into a validated MediaItem
    # (checks types, and shapes the JSON response with named fields)
    all_data = []
    for row in data:
        all_data.append(MediaItem(**dict(row)))

    conn.close()  # release the connection now that we're done with it

    return all_data


@app.get('/media/{id}')
def get_media_by_id(id: int):
    """Return a single media item by its id, or 404 if it doesn't exist."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # fetchone() since id is unique — there's at most one match
    item = cur.execute('SELECT * FROM media WHERE id = ?', (id,)).fetchone()
    conn.close()

    # fetchone() returns None if no row matched — that's our "not found" signal
    if item is None:
        raise HTTPException(status_code=404, detail='Media item not found')

    return MediaItem(**dict(item))


# dependencies=[Depends(verify_api_key)] — runs verify_api_key before this
# route's own code; write endpoints require a valid X-API-Key header
@app.patch('/media/{id}', dependencies=[Depends(verify_api_key)])
def patch_media_by_id(id: int, updates: MediaItemUpdate):
    """Partially update a media item — only fields present in the request
    body are changed; anything omitted is left untouched. 404 if the id
    doesn't exist. Requires a valid API key (see verify_api_key).
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    item = cur.execute('SELECT * FROM media WHERE id = ?', (id,)).fetchone()

    if item is None:
        conn.close()  # done with the connection either way — close before raising
        raise HTTPException(status_code=404, detail='Media item not found')

    # Only the fields actually present in the request body — not every
    # field, most of which will just be their unset default (None)
    fields_to_update = updates.model_dump(exclude_unset=True)

    # Build the SET clause dynamically, same pattern as the filters above
    condition = []
    values = []

    for column, value in fields_to_update.items():
        condition.append(f'{column} = ?')
        values.append(value)

    set_clause = ', '.join(condition)
    query = f'UPDATE media SET {set_clause} WHERE id = ?'
    values.append(id)  # matches the final ? in the WHERE clause

    cur.execute(query, values)
    conn.commit()
    conn.close()  # close here, after the update, since this is the other exit path

    return {'message': 'Media item updated'}


@app.delete('/media/{id}', dependencies=[Depends(verify_api_key)])
def delete_by_id(id: int):
    """Delete a single media item by its id, or 404 if it doesn't exist.
    Requires a valid API key (see verify_api_key).
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check existence first — DELETE never errors and never returns None,
    # even if no row matches, so it can't be used on its own to detect "not found"
    item = cur.execute('SELECT * FROM media WHERE id = ?', (id,)).fetchone()

    if item is None:
        conn.close()  # done with the connection either way — close before raising
        raise HTTPException(status_code=404, detail='Media item not found')

    # id is already confirmed valid from the SELECT above — reuse it directly,
    # SQL statements are independent, so this still needs its own WHERE clause
    cur.execute('DELETE FROM media WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return {'message': 'Media item deleted'}


@app.post('/media', status_code=201, dependencies=[Depends(verify_api_key)])
def post_media(new_media: MediaItemNew):
    """Create a new media item. id is not accepted from the client —
    SQLite auto-assigns it, since it's not in the column list below.
    Requires a valid API key (see verify_api_key).
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Row cap — protects the public demo (API key is published in the README,
    # so anyone can call this) from being flooded with junk data
    count = cur.execute('SELECT COUNT(*) FROM media').fetchone()[0]
    if count >= 50:
        conn.close()
        raise HTTPException(status_code=403, detail='Demo database is full — item limit reached')

    # model_dump() (no exclude_unset here) — every field either has a real
    # value or its default, since this is a full new record, not a partial update
    new_items = new_media.model_dump()
    values = list(new_items.values())

    query = 'INSERT INTO media (imdb_id, title, year, genres, runtime_mins, studio, tagline, description, tmdb_id, source, type, number_of_seasons, number_of_episodes, original_title, imdb_rating, release_date, directors, poster_path, "cast") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    cur.execute(query, values)

    # lastrowid — the id SQLite just auto-assigned to this new row
    new_item_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {"message": "Media item created", "id": new_item_id}