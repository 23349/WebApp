# My Ratings WebApp
from flask import Flask, g, render_template
import sqlite3

DATABASE = "database.db"

# Initializer
app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def home(): 
    # Gets the items for the scrollbar
    sql = """SELECT item.name, item.imgURL FROM item"""
    results = query_db(sql)
    return render_template("home.html", results=results)

@app.route('/login')
def login():
    sql = """SELECT * FROM user"""
    results = query_db(sql)
    print(results)
    return render_template("login.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
