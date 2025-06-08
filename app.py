from flask import Flask, render_template, request, redirect, session, url_for
import random
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Master list of NYC landmarks
landmarks_master = [
    "Statue of Liberty",
    "Central Park",
    "Times Square",
    "Brooklyn Bridge",
    "Rockefeller Center",
    "One World Trade Center",
    "Flatiron Building",
    "Grand Central Terminal",
    "High Line (Manhattan)",
    "Metropolitan Museum of Art"
]

# Fetch image from Wikipedia
def get_landmark_image(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    try:
        resp = requests.get(url).json()
        return resp.get("thumbnail", {}).get("source")
    except Exception:
        return None

@app.route("/")
def home():
    return render_template("start.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    if "remaining" not in session:
        session["remaining"] = landmarks_master.copy()
        random.shuffle(session["remaining"])
        session["score"] = 0
        session["total"] = len(landmarks_master)

    landmark = session.get("landmark")
    feedback = ""
    guessed_correctly = False
    last_question = False

    if not landmark and session["remaining"]:
        session["landmark"] = session["remaining"].pop()
        landmark = session["landmark"]

    image_url = get_landmark_image(landmark) if landmark else None

    if request.method == "POST":
        give_up = request.form.get("give_up")
        guess = request.form.get("guess")

        if landmark and (give_up or (guess and guess.strip())):
            if give_up:
                feedback = f"❌ The correct answer was: {landmark}."
            elif guess.strip().lower() == landmark.lower():
                session["score"] += 1
                feedback = f"🎉 Correct! It's {landmark}."
            else:
                feedback = f"❌ The correct answer was: {landmark}."

            guessed_correctly = True

            if not session["remaining"]:
                last_question = True

    return render_template(
        "index.html",
        image_url=image_url,
        feedback=feedback,
        guessed_correctly=guessed_correctly,
        last_question=last_question,
        score=session.get("score", 0),
        total=session.get("total", len(landmarks_master))
    )

@app.route("/next")
def next_landmark():
    session.pop("landmark", None)
    return redirect(url_for("game"))

@app.route("/summary")
def summary_page():
    return render_template("summary.html", score=session.get("score", 0), total=session.get("total", 0))

@app.route("/restart")
def restart_game():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
