from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

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
    conn = sqlite3.connect('./data/media.db')

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

    conn = sqlite3.connect('./data/media.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # fetchone() since id is unique — there's at most one match
    item = cur.execute('SELECT * FROM media WHERE id = ?', (id,)).fetchone()
    conn.close()

    # fetchone() returns None if no row matched — that's our "not found" signal
    if item is None:
        raise HTTPException(status_code=404, detail='Media item not found')

    return MediaItem(**dict(item))


@app.patch('/media/{id}')
def patch_media_by_id(id: int, updates: MediaItemUpdate):
    """Partially update a media item — only fields present in the request
    body are changed; anything omitted is left untouched. 404 if the id
    doesn't exist.
    """

    conn = sqlite3.connect('./data/media.db')
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


@app.delete('/media/{id}')
def delete_by_id(id: int):
    """Delete a single media item by its id, or 404 if it doesn't exist."""
 
    conn = sqlite3.connect('./data/media.db')
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