import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()

# cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
cur.execute('PRAGMA table_list')
columns = cur.fetchall()

for col in columns:
    print(col)

cur.execute('PRAGMA table_info(media)')
media_columns = cur.fetchall()

for col in media_columns:
    print(col)

conn.close()
print('Connection closed.')