# My Ratings WebApp
from flask import Flask, g, render_template, request, url_for, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

DATABASE = "database.db"

# Initializer
app = Flask(__name__)
app.secret_key = 'HELLFLAMEIGNITION'



def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
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

# add a decorator

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = query_db("SELECT * FROM user WHERE id = ?", [user_id], one=True)



# Gets the items for the scrollbar and renders home
@app.route('/')
def home(): 
    sql = """SELECT item.name, item.imgURL, item.item_id FROM item"""
    results = query_db(sql)
    return render_template("home.html", results=results)



# Gets the user information for the login page and renders it
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM user WHERE username = ?"
        user = query_db(sql, [username], one=True)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return "Invalid username or password"

    return render_template("login.html")



# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))



# Gets the user information for the register page and renders it
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash
        hashed_pw = generate_password_hash(password)
        
        query_db("INSERT INTO user (username, password) VALUES (?, ?)", [username, hashed_pw])
        return redirect(url_for('login'))
        
    return render_template("signup.html")



# Gets all the movies and their information
@app.route('/movies')
def movies():
    sql = """SELECT item.name, item.imgURL, item.item_id FROM item"""
    results = query_db(sql)
    return render_template("movies.html", results=results)



# Will get the information for the movie that is clicked on and render the page for it    
@app.route('/movies/<int:id>')
def individual_movie(id):
    sql = """SELECT * FROM item WHERE item.item_id = ?"""
    results = query_db(sql, (id,), True)
    return render_template("movie.html", movie=results)


if __name__ == "__main__":
    app.run(debug=True)
