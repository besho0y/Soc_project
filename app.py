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

@app.route("/network")
def network():
    return render_template("networkpage.html")

@app.route("/alerts")
def alerts():
    return render_template("alertspage.html")








if __name__=="__main__":
    app.run(debug=True)