from flask import Flask, render_template, request, redirect, session
import random
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session

# List of NYC landmarks
landmarks = [
    "Statue of Liberty",
    "Central Park",
    "Times Square",
    "Brooklyn Bridge",
    "Empire State Building",
    "Rockefeller Center",
    "One World Trade Center"
]

# Get image from Wikipedia API
def get_landmark_image(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    resp = requests.get(url).json()
    if "thumbnail" in resp:
        return resp["thumbnail"]["source"]
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if "landmark" not in session:
        session["landmark"] = random.choice(landmarks)

    landmark = session["landmark"]
    image_url = get_landmark_image(landmark)

    feedback = ""
    guessed_correctly = False

    if request.method == "POST":
        guess = request.form.get("guess", "").strip().lower()
        if guess == landmark.lower():
            feedback = f"🎉 Correct! It's {landmark}."
            guessed_correctly = True
        else:
            feedback = "❌ Try again!"

    return render_template("index.html", image_url=image_url, feedback=feedback, guessed_correctly=guessed_correctly)

@app.route("/reset")
def reset():
    session.pop("landmark", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)