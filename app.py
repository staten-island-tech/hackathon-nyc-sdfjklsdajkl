from flask import Flask, render_template, request, redirect, session, url_for
import random
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

landmarks_master = [
    "Statue of Liberty",
    "Central Park",
    "Times Square",
    "Brooklyn Bridge",
    "Rockefeller Center",
    "One World Trade Center",
    "Flatiron Building",
    "Chrysler Building",
    "Grand Central Terminal",
    "High Line (Manhattan)",
    "The Vessel (structure)",
    "Metropolitan Museum of Art"
]

def get_landmark_image(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    try:
        resp = requests.get(url).json()
        return resp.get("thumbnail", {}).get("source")
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if "remaining" not in session:
        session["remaining"] = landmarks_master.copy()
        random.shuffle(session["remaining"])
        session["score"] = 0
        session["total"] = len(landmarks_master)

    if "landmark" not in session and session["remaining"]:
        session["landmark"] = session["remaining"].pop()

    landmark = session.get("landmark")
    image_url = get_landmark_image(landmark) if landmark else None
    feedback = ""
    guessed_correctly = False
    game_over = False
    last_question = False
    round_complete = False

    if request.method == "POST":
        give_up = request.form.get("give_up")
        guess = request.form.get("guess", "").strip().lower()

        if landmark:
            if give_up:
                feedback = f"❌ The correct answer was: {landmark}."
            elif guess == landmark.lower():
                session["score"] += 1
                feedback = f"🎉 Correct! It's {landmark}."
            else:
                feedback = f"❌ The correct answer was: {landmark}."

            guessed_correctly = True
            round_complete = True

            if not session["remaining"]:
                last_question = True

    return render_template(
        "index.html",
        image_url=image_url,
        feedback=feedback,
        guessed_correctly=guessed_correctly,
        game_over=game_over,
        last_question=last_question,
        round_complete=round_complete,
        score=session.get("score", 0),
        total=session.get("total", len(landmarks_master))
    )

@app.route("/next")
def next_landmark():
    session.pop("landmark", None)
    return redirect(url_for("index"))

@app.route("/summary")
def summary_page():
    return render_template("summary.html", score=session.get("score", 0), total=session.get("total", 0))

@app.route("/restart")
def restart_game():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)