from flask import Flask, render_template
import json
from pathlib import Path

app = Flask(__name__)

# Pfad zur JSON-Datei
DATA_FILE = Path("blog_posts.json")

def load_posts():
    """Load all blog posts from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

@app.route('/')
def index():
    """Render the homepage with all blog posts."""
    blog_posts = load_posts()
    return render_template('index.html', posts=blog_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005, debug=True)