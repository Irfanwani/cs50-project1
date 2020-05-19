import os

import requests

from flask import Flask, render_template, session, request, jsonify, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.secret_key = "hello world"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    username = request.form.get("username")
    if request.method == "POST":
        session["username"] = username
        flash("Congrats! You joined successfully!", "info")
        return redirect(url_for("search"))
    else:
        if "username" in session:
            flash("Already logged in!", "info")
            return redirect(url_for("results"))
        return render_template("index.html")


@app.route("/login")
def login():
    if request.method == "POST":
        username1 = request.form.get("username1")
        session["username"] = username1
        flash("Congrats! You Logged in successfully!!", "info")
        return redirect(url_for("searches"))
    else:
        if "username" in session:
            flash("Already logged in!", "info")
            return redirect(url_for("results"))
        return render_template("login.html")


@app.route("/logout")
def logout():
    if "username" in session:
        username = session["username"]
        flash(f"{username}, You have been logged out!", "info")
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/search", methods=["GET", "POST"])
def search():
    search = request.form.get("search")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    users = db.execute("SELECT * FROM users")

    for user in users:
        if username == user.username or email == user.email:
            flash("Seems this username/email is already registered.Login here!", "info")
            return redirect(url_for("login"))

    if request.method == "POST":
        session["username"] = username
        flash("Congrats! You joined successfully!", "info")
        db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                   {"username": username, "email": email, "password": password})
        db.commit()
        books = db.execute(
            f"SELECT * FROM books WHERE isbn LIKE '%{search}%' OR title LIKE '%{search}%' OR author LIKE '%{search}%' OR publishyear LIKE '%{search}%'")
        return render_template("search.html", books=books)

    else:
        if "username" in session:
            flash("Already logged in!", "info")
            return redirect(url_for("results"))

    return render_template("loginfirst.html")


@app.route("/searches", methods=["GET", "POST"])
def searches():
    username1 = request.form.get("username1")
    password1 = request.form.get("password1")
    users = db.execute("SELECT * FROM users")
    books = db.execute("SELECT * FROM books")

    if request.method == "POST":
        for a_user in users:
            if username1 == a_user.username:
                user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username1}).fetchone()
                if password1 == user.password:
                    session["username"] = username1
                    flash("You logged in successfully!", "info")
                    return render_template("search.html", books=books)
                elif username1 != user.username or password1 != user.password:
                    flash("Username and/or password is incorrect.")
                    return redirect(url_for("login"))

    flash("Seems you are a new user. Register here!", "info")
    return redirect(url_for("index"))


@app.route("/results", methods=["GET", "POST"])
def results():
    search = request.form.get("search")

    if request.method == "GET":
        if "username" in session:
            flash("Please make a search.", "info")
        else:
            return render_template("loginfirst.html")

    books = db.execute(
        f"SELECT * FROM books WHERE isbn LIKE '%{search}%' OR title LIKE '%{search}%' OR author LIKE '%{search}%' OR publishyear LIKE '%{search}%'")

    if books is None:
        flash("No books found.Please make a proper search.", "info")
    return render_template("search.html", books=books)


@app.route("/bookdetails/<int:book_id>")
def bookdetails(book_id):
    if "username" in session:
        book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        isbn = db.execute("SELECT isbn FROM books WHERE id = :id", {"id": book_id}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "VShAUmmDnwjupqkKzEnNcw", "isbns": isbn})
        data = res.json()
        number_of_ratings = data["books"][0]["work_ratings_count"]
        av_ratings = data['books'][0]["average_rating"]
        return render_template("book.html", book=book, number_of_ratings=number_of_ratings, av_ratings=av_ratings)
    else:
        return render_template("loginfirst.html")


@app.route("/api/<string:isbn>")
def book_api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"Error": "Page not found! Seems you typed wrong ISBN number."}), 404

    isbn = db.execute("SELECT isbn FROM books WHERE id = :id", {"id": book.id}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "VShAUmmDnwjupqkKzEnNcw", "isbns": isbn})
    data = res.json()
    number_of_ratings = data["books"][0]["work_ratings_count"]
    av_ratings = data['books'][0]["average_rating"]

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.publishyear,
        "isbn": book.isbn,
        "review_count": number_of_ratings,
        "average_score": av_ratings
    })
