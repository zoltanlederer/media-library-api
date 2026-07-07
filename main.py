from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get('/media')
def read_root():
    conn = sqlite3.connect('./data/media.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM media')
    all_data = cur.fetchall()
    conn.close()
    return all_data

