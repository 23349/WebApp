# My Ratings WebAppand view other comments, fix the sign up and search, sql test
from flask import Flask, g, render_template, request, url_for, redirect, session, flash, jsonify, request
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


# Defines the query_db function that I'm gonna use throughout
def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# Sets the session for the user
@app.before_request
def load_logged_in_user():
    user = session.get('user')

    if user is None:
        g.user = None
    else:
        g.user = query_db("SELECT * FROM user WHERE user_id = ?", [user], one=True)



# 404 PAGE redirect
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



# Gets the items for the scrollbar and renders home
@app.route('/')
def home(): 
    sql = """SELECT item.name, item.imgURL, item.item_id FROM item"""
    sql2 = """SELECT item.name, item.imgURL, item.item_id FROM item ORDER BY item.item_id DESC"""
    results = query_db(sql)
    results2 = query_db(sql2)
    return render_template("home.html", results=results, results2=results2)



# Gets the user information for the login page and renders it
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Checks if the user has hit submit the login data and then processes it 
    if request.method == 'POST':

        # Grabs user input
        username = request.form['username']
        password = request.form['password']

        # gets the data for the username that the user entered
        sql = "SELECT * FROM user WHERE username = ?"
        user = query_db(sql, [username], one=True)

        # Checks if the password is correct for the user
        if user and check_password_hash(user['password'], password):
            session['user'] = user['user_id']
            return redirect(url_for('home'))
        else:
            flash("Username or password is incorrect ( o ⌓ o )", "login")
            return render_template("login.html", username=username)

    return render_template("login.html")



# You can leave...if you want to...but i hope you stay ( T - T )
@app.route('/logout')
def logout():
    session.clear()
    return redirect(request.referrer)



# Gets the user information for the register page and renders it
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    # Checks if the user has hit submit the sign up data and then processes it 
    if request.method == 'POST':

        # Grabs user input
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        email = request.form['email']

        # Username length constraint
        if len(username) > 64:
            flash("Username too long, max is 64 characters", "signup")
            return render_template("signup.html", email=email)

        # Password length contraint
        if len(password) <= 4: 
            flash("Password must be 4+ long", "signup")
            return render_template("signup.html", username=username, email=email)
            
        # Checks for a capital in the password
        if any(x.isupper() for x in password) == False:
            flash("Password must have a capital", "signup")
            return render_template("signup.html", username=username, email=email)

        # Checks if the two passwords are the same
        if password != confirm_password:
            flash("Passwords did not match ( o ⌓ o )", "signup")
            return render_template("signup.html", username=username, email=email)

        # Generates the new hashed password and add it as well as the other info to the user db
        hashed_pw = generate_password_hash(password)
        query_db("INSERT INTO user (username, password, email) VALUES (?, ?, ?)", [username, hashed_pw, email])
        return redirect(url_for('login'))
        
    return render_template("signup.html")



# Gets all the movies and their information
@app.route('/movies')
def movies():
    sql = "SELECT name, imgURL, item_id FROM item"
    results = query_db(sql)
    genres = query_db("SELECT name FROM genre")

    return render_template("movies.html", movies=results, genres=genres)



# An api that will allow the user to filter results without needing the page to refresh
@app.route('/api/movies')
def api_movies():

    # Gets the genre from the js in movies
    genreSelect = request.args.get("genre")

    if genreSelect:
        sql = """SELECT item.name, imgURL, item.item_id FROM item
        JOIN itemGenre ON item.item_id = itemGenre.item_id
        JOIN genre ON itemGenre.genre_id = genre.genre_id
        WHERE genre.name = ?"""
        raw_results = query_db(sql, (genreSelect,)) 
    else:
        sql = "SELECT name, imgURL, item_id FROM item"
        raw_results = query_db(sql)
    
    # A list to convert the results
    converted_results = []

    # Tuples --> dictionary
    if raw_results:
        for x in raw_results:
            converted_results.append({
                'name': x[0], 
                'imgURL': x[1],
                'item_id': x[2]
            })
            
    return jsonify(converted_results)



# Allows the user to search and if a single result is found it will take them directly to that page
@app.route('/search', methods=['GET', 'POST'])
def search():

    # Gets the values from the seachbar and removes any leading/trailing spaces
    search = request.values.get('searchbar', '').strip()
    if not search:
        # flashes error if nothing was entered
        flash("Please enter a search term.", "search_error")
        return redirect(request.referrer)

    sql = """SELECT item.name, item.imgURL, item.item_id FROM item WHERE item.name LIKE ?"""
    results = query_db(sql, [f"%{search}%"], False)

    # if there is only one results it returns it, flahshes nothing found
    if len(results) == 1:
        return redirect(url_for('individual_movie', id=results[0]['item_id']))
    if not results:
        flash(f"No results found for '{search}'", "search_error")
    return render_template("movies.html", results=results)



# Will get the information for the movie that is clicked on and render the page for it:
@app.route('/movies/<int:id>')
def individual_movie(id):
    sql = """SELECT * FROM item WHERE item_id = ?"""
    result = query_db(sql, (id,), one=True)

    # 404 if movie doesn't exist
    if result is None:
        return page_not_found(404)
    
    # Checks if the movie has a review
    sql = """SELECT AVG(rating) FROM ratings WHERE item_id = ?"""
    movie_review_check = query_db(sql, (id,), one=True)
    if movie_review_check and movie_review_check[0] is not None:
        movie_review_data = round(movie_review_check[0], 1)
    else:
        movie_review_data = None


    #sets the user data to nothing
    user_review_data = None

    # Checks if the user is logged in
    if g.user:
        sql = "SELECT * FROM ratings WHERE item_id = ? AND user_id = ?"

        # If they are, it will check if they have already left a review and then display it
        user_review_check = query_db(sql, (id, g.user['user_id']), one=True)
        if user_review_check:
            user_review_data = user_review_check
    else:
        flash("You must be logged in to review!", "review")

    return render_template("movie.html", movie=result, user_review=user_review_data, movie_rating=movie_review_data)



# Will allow the user to leave a review or eidt their old one
@app.route('/review', methods=['POST'])
def review():
    movie_id = request.form.get('movie_id')
    review_text = request.form.get('review')
    star_review = request.form.get('star')

    # sql to cehck if a review already exists and they are editing
    sql = """SELECT * FROM ratings WHERE user_id = ? AND item_id = ?"""
    existing_review = query_db(sql, (g.user['user_id'], movie_id))

    # if tyey already have a review it will update 
    if existing_review:
        sql = """UPDATE ratings SET review = ?, rating = ? WHERE user_id = ? AND item_id = ?"""
        query_db(sql,(review_text, star_review, g.user['user_id'], movie_id))

    # if they dont it will add one
    else:
        if star_review and movie_id:
            sql = """INSERT INTO ratings (review, user_id, item_id, rating) VALUES (?, ?, ?, ?)"""
            query_db(sql, (review_text, g.user['user_id'], movie_id, star_review))
    
    
    return redirect(url_for('individual_movie', id=movie_id))



if __name__ == "__main__":
    app.run(debug=True)
