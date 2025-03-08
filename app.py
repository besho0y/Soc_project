from flask import Flask, flash, json, jsonify, redirect, render_template, request, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_super_secret_key"

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database/AppData.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        points = user_data['points']
        done_scenarios = json.loads(user_data['done_scenarios'])  # Assuming this is a JSON string
        done_challenges = json.loads(user_data['done_challenges'])  # Assuming this is a JSON string
        total_scenarios = len(done_scenarios)
        total_challenges = len(done_challenges)
    else:
        username = "Guest"
        points = 0
        total_scenarios = 0
        total_challenges = 0

    return render_template("homepage/homepage.html", 
                           username=username, 
                           points=points, 
                           total_scenarios=total_scenarios, 
                           total_challenges=total_challenges)

# Scenarios page
@app.route("/scenario")
def scenario():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("homepage/scenariospage.html")

# Challenges page
@app.route("/challenges")
def challenges():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("homepage/challengespage.html")

# Achievements page
@app.route("/achievement")
def achievement():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("homepage/achievementpage.html")




























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

    if user_data:
        username = user_data['username']
        points = user_data['points']
        done_scenarios = json.loads(user_data['done_scenarios'])
        done_challenges = json.loads(user_data['done_challenges'])
        total_scenarios = len(done_scenarios)
        total_challenges = len(done_challenges)
        lvl = user_data['lvl']
    else:
        username = points = lvl = "N/A"
        total_scenarios = total_challenges = 0

    return render_template("homepage/profilepage.html", 
                           username=username, 
                           points=points, 
                           total_scenarios=total_scenarios, 
                           total_challenges=total_challenges, 
                           lvl=lvl)









@app.route("/api/challenges")
def get_challenges():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, points, duration, lvl FROM challenges")  # Adjust the query as needed
    challenges = cursor.fetchall()
    conn.close()

    # Convert the challenges to a list of dictionaries
    challenges_list = []
    for challenge in challenges:
        challenges_list.append({
            "title": challenge["title"],
            "description": challenge["description"],
            "points": challenge["points"],
            "duration": challenge["duration"],
            "lvl": challenge["lvl"]
        })

    return jsonify(challenges_list)  











if __name__ == "__main__":
    app.run(debug=True)
