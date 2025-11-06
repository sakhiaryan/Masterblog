from flask import Flask, render_template, request, redirect, url_for, flash, abort
import json
from pathlib import Path
import logging

# -------------------------------------------------
# App configuration
# -------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"
DATA_FILE = Path("blog_posts.json")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("masterblog")

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def load_posts():
    """Load posts safely from JSON file."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
    except (OSError, json.JSONDecodeError):
        flash("⚠️ Could not read blog data file.", "error")
        return []

def save_posts(posts):
    """Save posts safely to JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error(f"Error saving file: {e}")
        flash("❌ Could not save data.", "error")

def get_next_id(posts):
    """Generate unique incremental ID."""
    if not posts:
        return 1
    return max(p["id"] for p in posts) + 1

def find_post(posts, post_id):
    """Find post by ID."""
    for p in posts:
        if p["id"] == post_id:
            return p
    return None

def validate_post(title, content):
    """Basic input validation."""
    errors = []
    if not title or not title.strip():
        errors.append("Title is required.")
    if not content or not content.strip():
        errors.append("Content is required.")
    return errors

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route("/")
def index():
    """Homepage: list all posts."""
    posts = sorted(load_posts(), key=lambda p: p["id"], reverse=True)
    return render_template("index.html", posts=posts)

@app.route("/add", methods=["GET", "POST"])
def add():
    """Add a new post."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        posts = load_posts()
        errors = validate_post(title, content)

        # Check for duplicate title
        if any(p["title"].lower() == title.lower() for p in posts):
            errors.append("A post with this title already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("add.html", title=title, content=content), 400

        new_post = {"id": get_next_id(posts), "title": title, "content": content, "likes": 0}
        posts.append(new_post)
        save_posts(posts)
        flash("✅ Post added successfully.", "success")
        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    """Edit an existing post."""
    posts = load_posts()
    post = find_post(posts, post_id)
    if not post:
        abort(404, "Post not found.")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        errors = validate_post(title, content)

        # Prevent duplicate titles
        if any(p["title"].lower() == title.lower() and p["id"] != post_id for p in posts):
            errors.append("Another post with this title already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("update.html", post=post), 400

        post["title"] = title
        post["content"] = content
        save_posts(posts)
        flash("✏️ Post updated successfully.", "success")
        return redirect(url_for("index"))

    return render_template("update.html", post=post)

@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    """Delete a post."""
    posts = load_posts()
    post = find_post(posts, post_id)
    if not post:
        abort(404, "Post not found.")
    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    flash(f"🗑 Post #{post_id} deleted successfully.", "success")
    return redirect(url_for("index"))

@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    """Increment likes for a post."""
    posts = load_posts()
    post = find_post(posts, post_id)
    if not post:
        abort(404, "Post not found.")
    post["likes"] = post.get("likes", 0) + 1
    save_posts(posts)
    return redirect(url_for("index"))

# -------------------------------------------------
# Error Handlers (all using one template)
# -------------------------------------------------
@app.errorhandler(400)
def error_400(err):
    return render_template("error.html", code=400, title="Bad Request", message=str(err)), 400

@app.errorhandler(404)
def error_404(err):
    return render_template("error.html", code=404, title="Not Found", message=str(err)), 404

@app.errorhandler(405)
def error_405(err):
    return render_template("error.html", code=405, title="Method Not Allowed", message=str(err)), 405

@app.errorhandler(500)
def error_500(err):
    logger.exception("Server error: %s", err)
    return render_template("error.html", code=500, title="Server Error",
                           message="Something went wrong on the server."), 500

@app.errorhandler(Exception)
def error_generic(err):
    logger.exception("Unhandled exception: %s", err)
    return render_template("error.html", code=500, title="Server Error",
                           message="Unexpected error occurred."), 500

# -------------------------------------------------
# Run app
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)