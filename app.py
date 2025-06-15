from flask import Flask, flash, json, jsonify, redirect, render_template, request, url_for, session, abort
import sqlite3
from scenarios_data import SCENARIO_DETAILS

app = Flask(__name__)
app.secret_key = "your_super_secret_key"

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database/AppData.db')
    conn.row_factory = sqlite3.Row
    return conn

# Helper function to get scenario by slug
def get_scenario_by_slug(slug):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scenarios WHERE slug = ?", (slug,))
    scenario = cursor.fetchone()
    conn.close()
    return scenario

# Helper function to get all scenarios
def get_all_scenarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scenarios")
    scenarios = cursor.fetchall()
    conn.close()
    return scenarios

# Helper function to mark scenario as done
def mark_scenario_done(user_id, scenario_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if already marked as done
    cursor.execute("""
        SELECT COUNT(*) FROM done_scenarios 
        WHERE user_id = ? AND scenario_id = ?
    """, (user_id, scenario_id))
    
    if cursor.fetchone()[0] == 0:  # Not already marked as done
        cursor.execute("""
            INSERT INTO done_scenarios (user_id, scenario_id)
            VALUES (?, ?)
        """, (user_id, scenario_id))
        conn.commit()
    conn.close()

# Helper function to get user's done scenarios
def get_user_done_scenarios(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.* FROM scenarios s
        JOIN done_scenarios d ON s.id = d.scenario_id
        WHERE d.user_id = ?
    """, (user_id,))
    scenarios = cursor.fetchall()
    conn.close()
    return scenarios

# Intro page
@app.route("/")
def intropage():
    return render_template("intropage/intropage.html")

# Home page
@app.route("/home")
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Fetch user data
    email = session['user']
    user_data = get_user_data(email)
    
    if user_data:
        username = user_data['username']
        user_id = get_user_by_email(email)['id']
        
        # Get total scenarios count from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scenarios")
        total_scenarios_count = cursor.fetchone()[0]
        
        # Get user's achieved scenarios
        cursor.execute("""
            SELECT COUNT(DISTINCT scenario_id) FROM done_scenarios WHERE user_id = ?
        """, (user_id,))
        achieved_scenarios_count = cursor.fetchone()[0]
        
        # Calculate total points from achieved scenarios
        cursor.execute("""
            SELECT SUM(s.points) FROM scenarios s
            JOIN done_scenarios d ON s.id = d.scenario_id
            WHERE d.user_id = ?
        """, (user_id,))
        scenario_points_earned = cursor.fetchone()[0] or 0
        
        # Calculate total points from achieved challenges
        cursor.execute("""
            SELECT SUM(s.points) FROM scenarios s
            JOIN done_challenges dc ON s.slug = REPLACE(dc.challenge_slug, '-challenge', '')
            WHERE dc.user_id = ?
        """, (user_id,))
        challenge_points_earned = cursor.fetchone()[0] or 0
        
        achieved_points = scenario_points_earned + challenge_points_earned
        
        # Get total possible points from scenarios and challenges
        cursor.execute("SELECT SUM(points) FROM scenarios")
        scenario_total_points = cursor.fetchone()[0] or 0
        total_possible_points = scenario_total_points * 2  # Scenarios + Challenges
        
        conn.close()
        
        # Get challenges data (keeping existing logic for now)
        done_challenges = json.loads(user_data['done_challenges']) if user_data['done_challenges'] else []
        total_challenges = len(done_challenges)
        
    else:
        username = "Guest"
        achieved_scenarios_count = 0
        total_scenarios_count = 0
        achieved_points = 0
        total_possible_points = 0
        total_challenges = 0

    return render_template("homepage/homepage.html", 
                           username=username, 
                           achieved_scenarios=achieved_scenarios_count,
                           total_scenarios=total_scenarios_count,
                           achieved_points=achieved_points,
                           total_possible_points=total_possible_points,
                           total_challenges=total_challenges)

# Scenarios page
@app.route("/scenario")
def scenario():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']
    user_data = get_user_data(email)
    username = user_data['username'] if user_data else "Guest"
    
    return render_template("homepage/scenariospage.html", username=username)

# Challenges page
@app.route("/challenges")
def challenges():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']
    user_data = get_user_data(email)
    username = user_data['username'] if user_data else "Guest"
    
    return render_template("homepage/challengespage.html", username=username)

# Achievements page
@app.route("/achievement")
def achievement():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    email = session['user']
    user_data = get_user_data(email)
    username = user_data['username'] if user_data else "Guest"
    
    return render_template("homepage/achievementpage.html", username=username)

@app.route("/scenario/<slug>")
def scenario_detail(slug):
    scenario = get_scenario_by_slug(slug)
    if not scenario:
        abort(404)
    
    content = "<p>Scenario content not found.</p>"
    if scenario['content_file']:
        try:
            with open(scenario['content_file'], encoding='utf-8') as f:
                content = f.read()
        except Exception:
            pass

    # Get all scenarios for navigation
    scenarios = get_all_scenarios()
    slugs = [s['slug'] for s in scenarios]
    idx = slugs.index(slug) if slug in slugs else -1
    prev_slug = slugs[idx - 1] if idx > 0 else None
    next_slug = slugs[idx + 1] if idx < len(slugs) - 1 else None

    return render_template(
        "homepage/scenario_detail.html",
        scenario=scenario,
        content=content,
        prev_slug=prev_slug,
        next_slug=next_slug
    )

@app.route("/scenario/<slug>/complete", methods=["POST"])
def complete_scenario(slug):
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    scenario = get_scenario_by_slug(slug)
    if not scenario:
        return jsonify({"error": "Scenario not found"}), 404
    
    user_id = get_user_by_email(session['user'])['id']
    mark_scenario_done(user_id, scenario['id'])
    
    return jsonify({"success": True, "message": "Scenario marked as completed!"})

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                     (username, email, password))
        conn.commit()
        conn.close()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("login&signup/signup.html")

# Helper function to get user by email
def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)
        if user and user["password"] == password:  # Use 'password' column safely
            session['user'] = user["email"]  # Store email in session

            return redirect(url_for('home'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))

    return render_template("login&signup/login.html")

# Logout route
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Disable back navigation after login/logout
@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def get_user_data(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, points, done_scenarios, done_challenges, lvl 
        FROM users 
        WHERE email = ?
    """, (email,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

@app.route("/profile")
def user_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    user_data = get_user_data(email)
    user_id = get_user_by_email(email)['id']

    if user_data:
        username = user_data['username']
        points = user_data['points']
        
        # Get real scenarios data from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get completed scenarios count
        cursor.execute("""
            SELECT COUNT(DISTINCT scenario_id) FROM done_scenarios WHERE user_id = ?
        """, (user_id,))
        total_scenarios = cursor.fetchone()[0]
        
        # Get completed challenges count
        cursor.execute("""
            SELECT COUNT(*) FROM done_challenges WHERE user_id = ?
        """, (user_id,))
        total_challenges = cursor.fetchone()[0]
        
        # Calculate total possible points from scenarios and challenges (both use same scenarios table)
        cursor.execute("SELECT SUM(points) FROM scenarios")
        scenario_points = cursor.fetchone()[0] or 0
        total_possible_points = scenario_points * 2  # Scenarios + Challenges (same points)
        
        # Calculate user's total points from scenarios and challenges
        cursor.execute("""
            SELECT SUM(s.points) FROM scenarios s
            JOIN done_scenarios ds ON s.id = ds.scenario_id
            WHERE ds.user_id = ?
        """, (user_id,))
        scenario_points_earned = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT SUM(s.points) FROM scenarios s
            JOIN done_challenges dc ON s.slug = REPLACE(dc.challenge_slug, '-challenge', '')
            WHERE dc.user_id = ?
        """, (user_id,))
        challenge_points_earned = cursor.fetchone()[0] or 0
        
        total_points_earned = scenario_points_earned + challenge_points_earned
        
        # Determine user level based on points percentage
        if total_possible_points > 0:
            points_percentage = (total_points_earned / total_possible_points) * 100
            if points_percentage < 50:
                user_level = "Beginner"
                level_color = "beginner"
            elif points_percentage < 85:
                user_level = "Intermediate"
                level_color = "intermediate"
            else:
                user_level = "Advanced"
                level_color = "advanced"
        else:
            user_level = "Beginner"
            level_color = "beginner"
            points_percentage = 0
        
        # Get most recent completed scenario
        cursor.execute("""
            SELECT s.title, s.description, s.lvl, s.points, s.slug, ds.created_at
            FROM scenarios s
            JOIN done_scenarios ds ON s.id = ds.scenario_id
            WHERE ds.user_id = ?
            ORDER BY ds.created_at DESC
            LIMIT 1
        """, (user_id,))
        recent_scenario = cursor.fetchone()
        
        # Get most recent completed challenge
        cursor.execute("""
            SELECT dc.challenge_slug, s.title, s.lvl, s.points, dc.created_at
            FROM done_challenges dc
            JOIN scenarios s ON REPLACE(dc.challenge_slug, '-challenge', '') = s.slug
            WHERE dc.user_id = ?
            ORDER BY dc.created_at DESC
            LIMIT 1
        """, (user_id,))
        recent_challenge = cursor.fetchone()
        
        conn.close()
        
        # Determine the most recent activity
        recent_activity = None
        activity_type = None
        
        if recent_scenario and recent_challenge:
            # Compare timestamps to find the most recent
            if recent_scenario['created_at'] > recent_challenge['created_at']:
                recent_activity = recent_scenario
                activity_type = 'scenario'
            else:
                recent_activity = recent_challenge
                activity_type = 'challenge'
        elif recent_scenario:
            recent_activity = recent_scenario
            activity_type = 'scenario'
        elif recent_challenge:
            recent_activity = recent_challenge
            activity_type = 'challenge'
        
        lvl = user_data['lvl']
    else:
        username = points = lvl = "N/A"
        total_scenarios = total_challenges = 0
        recent_activity = None
        activity_type = None
        user_level = "Beginner"
        level_color = "beginner"
        total_possible_points = 0
        points_percentage = 0

    return render_template("homepage/profilepage.html", 
                           username=username, 
                           points=total_points_earned, 
                           total_scenarios=total_scenarios, 
                           total_challenges=total_challenges, 
                           lvl=lvl,
                           recent_activity=recent_activity,
                           activity_type=activity_type,
                           user_level=user_level,
                           level_color=level_color,
                           total_possible_points=total_possible_points,
                           points_percentage=points_percentage)









@app.route("/api/challenges")
def get_challenges():
    # Get scenarios from database and convert them to challenges
    scenarios = get_all_scenarios()
    challenges_list = [
        {
            "title": s["title"] + " Challenge",
            "description": s["description"],
            "points": s["points"],
            "duration": "30min",  # Default duration
            "lvl": s["lvl"],
            "img": s["img"],
            "slug": s["slug"] + "-challenge"
        }
        for s in scenarios
    ]
    return jsonify(challenges_list)







@app.route("/api/scenarios")
def get_scenarios():
    scenarios = get_all_scenarios()
    scenarios_list = [
        {
            "title": s["title"],
            "slug": s["slug"],
            "description": s["description"],
            "points": s["points"],
            "lvl": s["lvl"],
            "img": s["img"]
        }
        for s in scenarios
    ]
    return jsonify(scenarios_list)

@app.route("/api/achievements")
def get_achievements():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = get_user_by_email(session['user'])['id']
    done_scenarios = get_user_done_scenarios(user_id)
    
    return jsonify({
        "done_scenarios": [
            {
                "title": s["title"],
                "lvl": s["lvl"],
                "points": s["points"],
                "img": s["img"]
            }
            for s in done_scenarios
        ]
    })

@app.route("/api/done-challenges")
def get_done_challenges():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = get_user_by_email(session['user'])['id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dc.challenge_slug, s.title, s.lvl, s.points
        FROM done_challenges dc
        JOIN scenarios s ON REPLACE(dc.challenge_slug, '-challenge', '') = s.slug
        WHERE dc.user_id = ?
    """, (user_id,))
    
    done_challenges = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "done_challenges": [
            {
                "title": challenge["title"] + " Challenge",
                "level": challenge["lvl"],
                "points": challenge["points"]
            }
            for challenge in done_challenges
        ]
    })

# Helper function to get challenge questions based on scenario topic
def get_challenge_questions(scenario_slug):
    # Sample questions for different challenge topics
    questions_db = {
        "pass-the-hash-attack-defense": [
            {
                "question": "What is Pass-the-Hash attack primarily used for?",
                "options": ["Data encryption", "Lateral movement", "Password cracking", "Network scanning"],
                "correct": 1
            },
            {
                "question": "Which protocol is commonly targeted in Pass-the-Hash attacks?",
                "options": ["HTTP", "NTLM", "FTP", "SMTP"],
                "correct": 1
            },
            {
                "question": "What type of hash is typically used in Pass-the-Hash attacks?",
                "options": ["MD5", "SHA-256", "NTLM hash", "bcrypt"],
                "correct": 2
            },
            {
                "question": "Which tool is commonly used for Pass-the-Hash attacks?",
                "options": ["Nmap", "Mimikatz", "Wireshark", "Burp Suite"],
                "correct": 1
            },
            {
                "question": "How can you defend against Pass-the-Hash attacks?",
                "options": ["Use strong passwords", "Implement network segmentation", "Enable two-factor authentication", "All of the above"],
                "correct": 3
            }
        ],
        "scheduled-task-attack-defense": [
            {
                "question": "What is the primary purpose of scheduled tasks in Windows?",
                "options": ["Network communication", "Automated task execution", "File encryption", "User authentication"],
                "correct": 1
            },
            {
                "question": "Which Windows utility is used to manage scheduled tasks?",
                "options": ["Task Scheduler", "Event Viewer", "Registry Editor", "Control Panel"],
                "correct": 0
            },
            {
                "question": "How can attackers abuse scheduled tasks?",
                "options": ["For persistence", "For privilege escalation", "For lateral movement", "All of the above"],
                "correct": 3
            },
            {
                "question": "What file extension do scheduled task files typically have?",
                "options": [".exe", ".xml", ".bat", ".dll"],
                "correct": 1
            },
            {
                "question": "Which command can be used to list scheduled tasks?",
                "options": ["tasklist", "schtasks", "netstat", "systeminfo"],
                "correct": 1
            }
        ],
        "kerberoasting-attack-defense": [
            {
                "question": "What does Kerberoasting target?",
                "options": ["User passwords", "Service account tickets", "Network traffic", "File systems"],
                "correct": 1
            },
            {
                "question": "Which Kerberos ticket type is targeted in Kerberoasting?",
                "options": ["TGT", "TGS", "PAC", "KDC"],
                "correct": 1
            },
            {
                "question": "What is the main goal of Kerberoasting?",
                "options": ["Network scanning", "Password cracking", "Data exfiltration", "System monitoring"],
                "correct": 1
            },
            {
                "question": "Which tool is commonly used for Kerberoasting?",
                "options": ["Nmap", "GetUserSPNs.py", "Wireshark", "Metasploit"],
                "correct": 1
            },
            {
                "question": "How can you defend against Kerberoasting?",
                "options": ["Use strong service account passwords", "Monitor for unusual ticket requests", "Implement least privilege", "All of the above"],
                "correct": 3
            }
        ]
    }
    
    # Get questions for the specific challenge, or return default questions
    base_slug = scenario_slug.replace("-challenge", "")
    return questions_db.get(base_slug, [
        {
            "question": "What is the primary goal of cybersecurity?",
            "options": ["Data encryption", "Protecting information assets", "Network monitoring", "User training"],
            "correct": 1
        },
        {
            "question": "Which of the following is a common attack vector?",
            "options": ["Phishing", "Social engineering", "Malware", "All of the above"],
            "correct": 3
        },
        {
            "question": "What does CIA stand for in cybersecurity?",
            "options": ["Central Intelligence Agency", "Confidentiality, Integrity, Availability", "Computer Information Access", "Cyber Intelligence Analysis"],
            "correct": 1
        },
        {
            "question": "Which is the best practice for password security?",
            "options": ["Use simple passwords", "Reuse passwords", "Use complex, unique passwords", "Share passwords"],
            "correct": 2
        },
        {
            "question": "What is the purpose of a firewall?",
            "options": ["Data backup", "Network traffic filtering", "Password management", "File encryption"],
            "correct": 1
        }
    ])

# Helper function to mark challenge as done
def mark_challenge_done(user_id, challenge_slug):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if already marked as done
    cursor.execute("""
        SELECT COUNT(*) FROM done_challenges 
        WHERE user_id = ? AND challenge_slug = ?
    """, (user_id, challenge_slug))
    
    if cursor.fetchone()[0] == 0:  # Not already marked as done
        cursor.execute("""
            INSERT INTO done_challenges (user_id, challenge_slug)
            VALUES (?, ?)
        """, (user_id, challenge_slug))
        conn.commit()
    conn.close()

@app.route("/api/challenge/<slug>/questions")
def get_challenge_quiz(slug):
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    questions = get_challenge_questions(slug)
    # Return questions without correct answers for security
    quiz_questions = [
        {
            "id": i,
            "question": q["question"],
            "options": q["options"]
        }
        for i, q in enumerate(questions)
    ]
    
    return jsonify({"questions": quiz_questions})

@app.route("/api/challenge/<slug>/submit", methods=["POST"])
def submit_challenge_quiz(slug):
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    user_answers = data.get('answers', [])
    
    questions = get_challenge_questions(slug)
    correct_count = 0
    
    for i, answer in enumerate(user_answers):
        if i < len(questions) and answer == questions[i]["correct"]:
            correct_count += 1
    
    passed = correct_count >= 3
    
    if passed:
        user_id = get_user_by_email(session['user'])['id']
        mark_challenge_done(user_id, slug)
    
    return jsonify({
        "passed": passed,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "message": f"You got {correct_count} out of {len(questions)} correct. {'Congratulations! Challenge completed!' if passed else 'You need at least 3 correct answers to pass.'}"
    })

@app.route("/quiz")
def quiz_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("homepage/quiz.html")

if __name__ == "__main__":
    app.run(debug=True)
