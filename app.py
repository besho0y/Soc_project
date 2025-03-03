from flask import Flask,render_template,url_for

app =Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/scenario")
def scenario():
    return render_template("scenariopage.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/alerts")
def alerts():
    return render_template("alertspage.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")








if __name__=="__main__":
    app.run(debug=True)