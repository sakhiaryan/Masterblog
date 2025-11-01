from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path("blog_posts.json")

def load_posts():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4)

@app.route("/")
def index():
    posts = load_posts()
    return render_template("index.html", posts=posts)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Formularwerte auslesen
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        # Bestehende Beiträge laden
        posts = load_posts()

        # Neue ID bestimmen (höchste ID + 1)
        new_id = max([p["id"] for p in posts], default=0) + 1

        # Neuen Beitrag hinzufügen
        new_post = {
            "id": new_id,
            "author": author,
            "title": title,
            "content": content
        }
        posts.append(new_post)
        save_posts(posts)

        # Zurück zur Startseite
        return redirect(url_for("index"))

    return render_template("add.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)