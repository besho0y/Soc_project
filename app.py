from flask import Flask,render_template,url_for

app =Flask(__name__)


@app.route("/")
def intropage():
    return render_template("intropage/intropage.html")



@app.route("/home")
def home():
    return render_template("homepage/homepage.html")


@app.route("/scenario")
def scenario():
    return render_template("homepage/scenariospage.html")

@app.route("/challenges")
def challenges():
    return render_template("homepage/challengespage.html")


@app.route("/achievement")
def achievement():
    return render_template("homepage/achievementpage.html")












@app.route("/signup")
def signup():
    return render_template("login&signup/signup.html")


@app.route("/login")
def login():
    return render_template("login&signup/login.html")





if __name__=="__main__":
    app.run(debug=True)