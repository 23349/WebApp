# My Ratings WebApp
from flask import Flask, g, render_template, request, url_for, redirect, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

DATABASE = "database.db"

# Initializer
app = Flask(__name__)
app.secret_key = 'FINALSPARK-HELLFLAMEIGNITION'



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
    db = get_db()
    cur = get_db().execute(query, args)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = query_db("SELECT * FROM user WHERE user_id = ?", [user_id], one=True)



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
            session['user_id'] = user['user_id']
            return redirect(url_for('home'))
        else:
            flash(" Invalid Username or Password ( O - O ) ", "error")
            return render_template("login.html", username=username)

    return render_template("login.html")


# You can leave...if you want to...but i hope you stay ( T - T )
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



# Gets the user information for the register page and renders it
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        email = request.form['email']
        
        if password != confirm_password:
            flash("Passwords did not match ( o ⌓ o ) ", "error")
            return render_template("signup.html", username=username, email=email)
        
        hashed_pw = generate_password_hash(password)
        query_db("INSERT INTO user (username, password, email) VALUES (?, ?, ?)", [username, hashed_pw, email])
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



@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.values.get('searchbar', '').strip()
    if not query:
        flash("Please enter a search term.", "error")
        return redirect(url_for('home'))

    sql = """SELECT item.name, item.imgURL, item.item_id FROM item WHERE item.name LIKE ?"""
    results = query_db(sql, [f"%{query}%"], False)

    if len(results) == 1:
        return redirect(url_for('individual_movie', id=results[0]['item_id']))
    if not results:
        flash(f"No results found for '{query}'", "error")
    return render_template("movies.html", results=results)


@app.route('/review', methods=['GET', 'POST'])
def review():
    review = request.values.get('review')
    query_db("INSERT INTO ratings (review) VALUES (?)", [review])



if __name__ == "__main__":
    app.run(debug=True)
