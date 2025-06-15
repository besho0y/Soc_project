import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from scenarios_data import SCENARIO_DETAILS

def migrate_scenarios():
    conn = sqlite3.connect('database/AppData.db')
    cursor = conn.cursor()

    # Clear existing scenarios
    cursor.execute("DELETE FROM scenarios")
    
    # Insert scenarios from SCENARIO_DETAILS
    for slug, scenario in SCENARIO_DETAILS.items():
        cursor.execute("""
            INSERT INTO scenarios (title, points, description, lvl, img, slug, content_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            scenario['title'],
            scenario['points'],
            scenario['description'],
            scenario['lvl'],
            scenario['img'],
            slug,
            scenario.get('content_file')
        ))
    
    conn.commit()
    conn.close()
    print("Scenarios migrated successfully!")

if __name__ == "__main__":
    migrate_scenarios() 