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

# 🔥 Neue Route zum Löschen eines Posts
@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    posts = load_posts()
    # Filtert alle Posts außer dem mit der passenden ID
    updated_posts = [p for p in posts if p["id"] != post_id]
    save_posts(updated_posts)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007, debug=True)