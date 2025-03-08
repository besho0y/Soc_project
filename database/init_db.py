import sqlite3

conn = sqlite3.connect('database/AppData.db')


cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    points INTEGER,
    done_scenarios TEXT,
    done_challenges TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    points INTEGER,
    description TEXT,
    duration INTEGER,
    lvl TEXT         
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    points INTEGER,
    description TEXT,  
    lvl TEXT,
    img TEXT
)
''')

conn.commit()
conn.close()

print("Database initialized and table created!")
