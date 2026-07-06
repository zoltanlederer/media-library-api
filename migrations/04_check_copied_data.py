import sqlite3

conn = sqlite3.connect('../data/media.db')
cur = conn.cursor()

media_table_count = cur.execute('SELECT COUNT(*) FROM media').fetchone()
media_new_table_count = cur.execute('SELECT COUNT(*) FROM media_new').fetchone()

print(f"Number of rows for media table: {media_table_count[0]}")
print(f"Number of rows for media_new table: {media_new_table_count[0]}")
print("*" * 10)

media_table = cur.execute('SELECT * FROM media LIMIT 1').fetchall()
media_new_table = cur.execute('SELECT * FROM media_new LIMIT 1').fetchall()

print(media_table)
print(media_new_table)

conn.close()