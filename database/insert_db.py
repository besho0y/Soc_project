import sqlite3

from flask import json

# Connect to SQLite database
conn = sqlite3.connect("database/AppData.db")

# Create a cursor object
cursor = conn.cursor()

# # # insert
# cursor.execute(
#     """
#     INSERT INTO scenarios (title, points, description,lvl,img)
#     VALUES (?, ?, ?, ?,?)
# """,
#     ("SQL Injection Attack", 30, "cyberattack that injects malicious SQL code into an application, allowing the attacker to view or modify a database", "Hard", 'static/images/sqlinjection.jpg'),
# # )
# print("added")
# print("done")

cursor.execute("DROP TABLE done_scenarios;")


# # get
# cursor.execute("SELECT * FROM scenarios")
# print(cursor.fetchall())


# Commit changes and close the connection
conn.commit()
conn.close()
