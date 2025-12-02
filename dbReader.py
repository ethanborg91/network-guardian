import sqlite3

conn = sqlite3.connect('devices.db')
c = conn.cursor()
c.execute("SELECT * FROM devices")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()