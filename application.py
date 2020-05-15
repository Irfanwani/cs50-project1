import os

import requests

from flask import Flask, render_template, session, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
Session = scoped_session(sessionmaker(bind=engine))
db = Session()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    search = request.form.get("search")
    books = db.execute(
        f"SELECT * FROM books WHERE isbn LIKE '%{search}%' OR title LIKE '%{search}%' OR author LIKE '%{search}%' OR publishyear LIKE '%{search}%'")
    return render_template("search.html", books=books)


@app.route("/bookdetails/<int:book_id>")
def bookdetails(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    isbn = db.execute("SELECT isbn FROM books WHERE id = :id", {"id": book_id}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "VShAUmmDnwjupqkKzEnNcw", "isbns": isbn})
    data = res.json()
    number_of_ratings = data["books"][0]["work_ratings_count"]
    av_ratings = data['books'][0]["average_rating"]
    return render_template("book.html", book=book, number_of_ratings=number_of_ratings, av_ratings=av_ratings)

