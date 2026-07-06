import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()

cur.execute('PRAGMA table_info(media_new)')
columns = cur.fetchall()

for col in columns:
    print(col)

conn.close()
print('Connection closed.')