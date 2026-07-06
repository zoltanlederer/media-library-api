import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()

cur.execute("DROP TABLE media")
cur.execute("ALTER TABLE media_new RENAME TO media")

conn.commit()
conn.close()
print('Table renamed.')