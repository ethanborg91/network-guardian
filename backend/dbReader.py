import sqlite3

conn = sqlite3.connect('scanner/test_devices.db')
c = conn.cursor()
c.execute("SELECT * FROM devices")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()