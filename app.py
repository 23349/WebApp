"""My Ratings WebApp - search, sql test."""

import sqlite3
import os
from functools import wraps

from flask import (
    Flask,
    g,
    render_template,
    request,
    url_for,
    redirect,
    session,
    flash,
    jsonify,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

DATABASE = "database.db"
load_dotenv()

# Initializer
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# FINALSPARK-HELLFLAMEIGNITION
""" HELLFLAMEIGNITION is an Archangel Uriel (Demon-like Judge of Fire),
Jung Heewon (Judge of Chaos) and The Living Flame (Outer God version
of Uriel from regression 999) reference from ORV, since only they
share the extremely powerful stigma HELLFLAME. 
FINALSPARK refrences Uriels final stand against The Ancient Dream where 
she uses her dying embers of  HELLFLAME to ignite and fight against 
The Ancient Dream until her flame  (life) eventually burnt out and see 
reached her plausible //end// stated by the STAR STREAM.
This refrence is in my project becasue I'm reading ORV right and lovin' it """

csrf = CSRFProtect(app)
""" csrf protects my website by basically restriciting who can submit 
a request since the required csrf will be embedded into my page."""

def get_db():
    """Return the request-scoped SQLite connection, creating it if needed."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(_exception):
    """Close the database connection at the end of the request."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Run a query and return either a single row or all rows."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.before_request
def load_logged_in_user():
    """Load the logged-in user (if any) into ``g.user`` for this request."""
    user = session.get("user")

    if user is None:
        g.user = None
    else:
        g.user = query_db("SELECT * FROM user WHERE user_id = ?", [user], one=True)


@app.errorhandler(404)
def page_not_found(_error):
    """Renders the custom 404 page."""
    return render_template("404.html"), 404

def login_required(function):
    """A decorator that require the user to be logged in before accessing a route"""
    @wraps(function)
    # Wraps lets me keep the function data by keeping its name instead of changing it to wrapper
    def wrapper(*args, **kwargs):
    # I dont really need args and kwargs since I'm only implementing this into /review
        if g.user is None:
            flash("You must be logged in to do that", "login")
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    """Get the items for the scrollbar and render the home page."""
    sql = "SELECT item.name, item.imgURL, item.item_id FROM item"
    sql2 = """SELECT item.name, item.imgURL, item.item_id FROM item
              ORDER BY item.item_id DESC"""
    results = query_db(sql)
    results2 = query_db(sql2)
    return render_template("home.html", results=results, results2=results2)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Get the user info for the login page and render it."""
    # Checks if the user has hit submit on the login form and processes it.
    if request.method == "POST":
        # Grabs user input.
        username = request.form["username"]
        password = request.form["password"]

        # Gets the data for the username that the user entered.
        sql = "SELECT * FROM user WHERE username = ?"
        user = query_db(sql, [username], one=True)

        # Checks if the password is correct for the user.
        if user and check_password_hash(user["password"], password):
            session["user"] = user["user_id"]
            return redirect(url_for("home"))

        flash("Username or password is incorrect ( o \u2313 o )", "login")
        return render_template("login.html", username=username)

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log the user out and send them back where they came from."""
    session.clear()
    return redirect((request.referrer) or url_for("home"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Get the user info for the register page and render it."""
    # Checks if the user has hit submit on the sign-up form and processes it.
    if request.method == "POST":
        # Grabs user input.
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        email = request.form["email"]

        # Username length constraint.
        if len(username) > 64:
            flash("Username too long, max is 64 characters", "signup")
            return render_template("signup.html", email=email)

        # Password length constraint.
        if len(password) <= 4:
            flash("Password must be 4+ long", "signup")
            return render_template("signup.html", username=username, email=email)

        # Checks for a capital letter in the password.
        if not any(x.isupper() for x in password):
            flash("Password must have a capital", "signup")
            return render_template("signup.html", username=username, email=email)

        # Checks if the two passwords match.
        if password != confirm_password:
            flash("Passwords did not match ( o \u2313 o )", "signup")
            return render_template("signup.html", username=username, email=email)

        # Generates the hashed password and adds it plus the other info
        # to the user table.
        hashed_pw = generate_password_hash(password)
        query_db(
            "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
            [username, hashed_pw, email],
        )
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/movies")
def movies():
    """Get all the movies and their information."""
    sql = "SELECT name, imgURL, item_id FROM item"
    results = query_db(sql)
    genres = query_db("SELECT name FROM genre")

    return render_template("movies.html", movies=results, genres=genres)


@app.route("/api/movies")
def api_movies():
    """Filter results for the movies page without needing a full refresh."""
    # Gets the genre from the JS in movies.html.
    genre_select = request.args.get("genre")

    if genre_select:
        sql = """SELECT item.name, imgURL, item.item_id FROM item
                 JOIN itemGenre ON item.item_id = itemGenre.item_id
                 JOIN genre ON itemGenre.genre_id = genre.genre_id
                 WHERE genre.name = ?"""
        raw_results = query_db(sql, (genre_select,))
    else:
        sql = "SELECT name, imgURL, item_id FROM item"
        raw_results = query_db(sql)

    # A list to hold the converted results.
    converted_results = []

    # Tuples --> dictionary.
    if raw_results:
        for result in raw_results:
            converted_results.append(
                {
                    "name": result[0],
                    "imgURL": result[1],
                    "item_id": result[2],
                }
            )

    return jsonify(converted_results)


@app.route("/search", methods=["GET", "POST"])
def search():
    """Search movies; redirect straight to the page if there's one match."""
    # Gets the value from the search bar and strips leading/trailing spaces.
    search_term = request.values.get("searchbar", "").strip()
    if not search_term:
        # Flashes an error if nothing was entered.
        flash("Please enter a search term.", "search_error")
        return redirect(request.referrer)

    sql = "SELECT item.name, item.imgURL, item.item_id FROM item WHERE item.name LIKE ?"
    results = query_db(sql, [f"%{search_term}%"], False)

    # If there is only one result, redirect straight to it.
    if len(results) == 1:
        return redirect(url_for("individual_movie", movie_id=results[0]["item_id"]))
    if not results:
        flash(f"No results found for '{search_term}'", "search_error")
    return render_template("movies.html", movies=results)


@app.route("/movies/<int:movie_id>")
def individual_movie(movie_id):
    """Get the information for the requested movie and render its page."""
    sql = "SELECT * FROM item WHERE item_id = ?"
    result = query_db(sql, (movie_id,), one=True)

    # 404 if the movie doesn't exist.
    if result is None:
        return page_not_found(404)

    # Checks if the movie has a review.
    sql = "SELECT AVG(rating) FROM ratings WHERE item_id = ?"
    movie_review_check = query_db(sql, (movie_id,), one=True)
    if movie_review_check and movie_review_check[0] is not None:
        # Rounds the average to 1 decimal place.
        movie_review_data = round(movie_review_check[0], 1)
    else:
        movie_review_data = None

    # Sets the user's own review data to nothing by default.
    user_review_data = None

    # Checks if the user is logged in.
    if g.user:
        sql = "SELECT * FROM ratings WHERE item_id = ? AND user_id = ?"

        # If they are, checks whether they've already left a review.
        user_review_check = query_db(sql, (movie_id, g.user["user_id"]), one=True)
        if user_review_check:
            user_review_data = user_review_check
    else:
        flash("You must be logged in to review!", "review")

    if g.user:
        sql = """SELECT ratings.*, user.username FROM ratings
                 JOIN user ON ratings.user_id = user.user_id
                 WHERE item_id = ? AND ratings.user_id <> ?"""
        all_movie_reviews = query_db(sql, (movie_id, g.user["user_id"]))
    else:
        sql = """SELECT ratings.*, user.username FROM ratings
                 JOIN user ON ratings.user_id = user.user_id
                 WHERE item_id = ?"""
        all_movie_reviews = query_db(sql, (movie_id,))

    return render_template(
        "movie.html",
        movie=result,
        user_review=user_review_data,
        movie_rating=movie_review_data,
        reviews=all_movie_reviews,
    )


@app.route("/review", methods=["POST"])
@login_required
def review():
    """Let the user leave a review, or edit their existing one."""
    movie_id = request.form.get("movie_id")
    review_text = request.form.get("review")
    star_review = request.form.get("star")

    # Checks if a review already exists (i.e. they're editing).
    sql = "SELECT * FROM ratings WHERE user_id = ? AND item_id = ?"
    existing_review = query_db(sql, (g.user["user_id"], movie_id))

    # If they already have a review, update it.
    if existing_review:
        sql = """UPDATE ratings SET review = ?, rating = ?
                 WHERE user_id = ? AND item_id = ?"""
        query_db(sql, (review_text, star_review, g.user["user_id"], movie_id))
    # Otherwise, insert a new one.
    elif star_review and movie_id:
        sql = """INSERT INTO ratings (review, user_id, item_id, rating)
                 VALUES (?, ?, ?, ?)"""
        query_db(sql, (review_text, g.user["user_id"], movie_id, star_review))

    return redirect(url_for("individual_movie", movie_id=movie_id))


if __name__ == "__main__":
    app.run(debug=True)
