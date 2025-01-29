from flask import Flask,render_template,url_for

app =Flask(__name__)
lessons=[
    {
    "title":"hello",
    "course":"english",
    "instructor":"ahmed"
},
    {
    "title":"alphabet",
    "course":"arabic",
    "instructor":"me"
},
    {
    "title":"math1",
    "course":"math",
    "instructor":"ali"
},

]

@app.route("/")
def home():
    return render_template("home.html",lessons=lessons)

@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/scenario")
def scenario():
    return render_template("scenariopage.html")

@app.route("/network")
def network():
    return render_template("networkpage.html")

@app.route("/alerts")
def alerts():
    return render_template("alertspage.html")








if __name__=="__main__":
    app.run(debug=True)