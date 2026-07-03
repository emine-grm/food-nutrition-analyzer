"""
app.py — serves the Emina frontend.

Routes match the filenames used in the HTML's own <a href="..."> links
(e.g. login.html, dashboard.html), so no navigation markup had to change
when moving from static files into Flask templates.
"""
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def landing():
    return render_template("index.html")


@app.route("/login.html")
def login():
    return render_template("login.html")


@app.route("/signup.html")
def signup():
    return render_template("signup.html")


@app.route("/onboarding.html")
def onboarding():
    return render_template("onboarding.html")


@app.route("/dashboard.html")
def dashboard():
    return render_template("dashboard.html")


@app.route("/analyze.html")
def analyze():
    return render_template("analyze.html")


@app.route("/results.html")
def results():
    return render_template("results.html")


@app.route("/history.html")
def history():
    return render_template("history.html")


@app.route("/profile.html")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    app.run(debug=True)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": blip_model is not None
    }
