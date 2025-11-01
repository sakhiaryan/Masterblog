from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path("blog_posts.json")

# ---- JSON Handling ----
def load_posts():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4)

# ---- Routes ----
@app.route("/")
def index():
    posts = load_posts()
    return render_template("index.html", posts=posts)

@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        posts = load_posts()
        new_id = max([p["id"] for p in posts], default=0) + 1
        posts.append({
            "id": new_id,
            "author": author,
            "title": title,
            "content": content,
            "likes": 0
        })
        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/delete/<int:post_id>")
def delete(post_id):
    posts = load_posts()
    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    return redirect(url_for("index"))

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        post["author"] = request.form.get("author")
        post["title"] = request.form.get("title")
        post["content"] = request.form.get("content")

        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("update.html", post=post)

@app.route("/like/<int:post_id>")
def like(post_id):
    posts = load_posts()
    for post in posts:
        if post["id"] == post_id:
            post["likes"] += 1
    save_posts(posts)
    return redirect(url_for("index"))

# ---- Run App ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)