from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path

app = Flask(__name__)

# === Speicherdatei für Blog-Posts ===
DATA_FILE = Path("blog_posts.json")


# ---------- Hilfsfunktionen ----------
def load_posts():
    """Lädt alle Blogposts aus der JSON-Datei."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posts(posts):
    """Speichert alle Blogposts in der JSON-Datei."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4)


# ---------- ROUTES ----------
@app.route("/")
def index():
    """Startseite: zeigt alle Blogposts an."""
    posts = load_posts()
    return render_template("index.html", posts=posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Route zum Hinzufügen eines neuen Posts."""
    if request.method == "POST":
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        posts = load_posts()
        new_id = max([p["id"] for p in posts], default=0) + 1
        new_post = {"id": new_id, "author": author, "title": title, "content": content}

        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("add.html")
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        posts = load_posts()
        new_id = max([p["id"] for p in posts], default=0) + 1
        new_post = {
            "id": new_id,
            "author": author,
            "title": title,
            "content": content,
            "likes": 0  # ❤️ Neues Feld
        }

        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    """Route zum Löschen eines Posts."""
    posts = load_posts()
    updated_posts = [p for p in posts if p["id"] != post_id]
    save_posts(updated_posts)
    return redirect(url_for("index"))

@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    """Erhöht die Like-Zahl eines Posts um 1."""
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if post is None:
        return "Post not found", 404

    post["likes"] = post.get("likes", 0) + 1
    save_posts(posts)
    return redirect(url_for("index"))

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    """Route zum Bearbeiten eines vorhandenen Posts."""
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        # Daten aus dem Formular holen
        post["author"] = request.form.get("author")
        post["title"] = request.form.get("title")
        post["content"] = request.form.get("content")

        # Datei aktualisieren
        save_posts(posts)
        return redirect(url_for("index"))

    # GET-Anfrage: Formular mit bestehenden Werten anzeigen
    return render_template("update.html", post=post)


# ---------- START SERVER ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)