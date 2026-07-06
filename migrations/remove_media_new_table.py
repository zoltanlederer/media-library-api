import sqlite3
conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()
cur.execute("DROP TABLE media_new")
conn.commit()
conn.close()
print("media_new dropped.")