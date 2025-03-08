import sqlite3

from flask import json

# Connect to SQLite database
conn = sqlite3.connect("database/AppData.db")

# Create a cursor object
cursor = conn.cursor()

# insert
# cursor.execute('''
#     INSERT INTO challenges (title, points, description, duration,lvl)
#     VALUES (?, ?, ?, ?,?)
# ''', ("forth scenario", 20, "scenarios des", 20,"medium"))


# get
cursor.execute("SELECT * FROM challenges")
print(cursor.fetchall())



# Commit changes and close the connection
conn.commit()
conn.close()
