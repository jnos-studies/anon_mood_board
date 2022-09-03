import os
import secrets
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from authentication import login_required, apology
from datetime import datetime as date
from free_apis import get_random_quote as quote
from image_generator import make_mood_image as moodI

import re

# importing custom config file
import config

def create_app(testing: bool = True):

    app = Flask(__name__)
    # configure session to use filesystem (instead of signed cookies)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # Testing database to be used before production database
    db = SQL("sqlite:///test_data.db")

    @app.after_request
    def after_request(response):
        # Ensure responses are not cached
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        response.headers["SameSite"] = "Strict"
        return response
    # User home page will show them how many times they logged their mood,
    # There generated mood color, how many users share similar moods,
    # And others
    @app.route("/")
    @login_required
    def index():
        # Get username
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        # Get user's mood image to display
        user_image_path = "static/mood_images/" + db.execute("SELECT path_to_img FROM users WHERE id = ?", session["user_id"])[0]["path_to_img"] + ".png"
        # Get user moods
        moods = db.execute("SELECT rating, date FROM moods WHERE user_id = ?", session["user_id"])
        average_feels = int(db.execute("SELECT avg(rating) AS average FROM moods WHERE user_id = ?", session["user_id"])[0]["average"])
        return render_template("index.html", image_path=user_image_path, username=username[0]["username"], moods=moods, rgb=config.RGB_SCHEME_MAP)

    @app.route("/log_mood", methods=["GET","POST"])
    @login_required
    def log_mood():
        # Get number of users logged moods
        moods = db.execute("SELECT date FROM moods WHERE user_id = ?", session["user_id"])
        num_logged_moods = len(moods)

        # Get user image path to overwrite their picture with their averaged mood.
        user_image_path = db.execute("SELECT path_to_img FROM users WHERE id = ?", session["user_id"])[0]["path_to_img"]

        # For checking the log limit, reject request if user exceeds their daily limit
        current_date = date.now()
        limit = config.LOG_LIMIT
        timedeltas = ""
        # Limit is defined in seconds for accuracy. Check that the last two logs are within limit, if number of logs is less than 2, timedelta equals the limit, allowing log of moods
        if num_logged_moods >= 2:
            timedeltas = [(current_date - date.strptime(moods[-2:][0]["date"],"%Y-%m-%d %H:%M:%S")).total_seconds(), (current_date - date.strptime(moods[-2:][1]["date"],"%Y-%m-%d %H:%M:%S")).total_seconds()]
        else:
            timedeltas = [limit, limit]
        # TODO Set a limit on how many logs a user can perform per day (2 per day), and set it to the machine time on server
        if request.method == "POST":
            if timedeltas[0] < limit and timedeltas[1] < limit:
                next_log = round(limit - timedeltas[1])
                flash("You can only log 2 moods per day! Time until next available log is {} seconds, {} minutes, or {} hours!!".format(next_log, round(next_log / 60, 2), round((next_log / 60) / 60), 2))
            else:
                rating = request.form["inlineRadioOptions"]
                db.execute("INSERT INTO moods(user_id, rating) VALUES(?, ?)", session["user_id"], rating)
                average_feels = int(db.execute("SELECT avg(rating) AS average FROM moods WHERE user_id = ?", session["user_id"])[0]["average"])
                moodI(user_image_path, rgb=config.RGB_SCHEME_MAP[average_feels])

                return redirect("log_mood")
        return render_template("log_mood.html", log_nums=num_logged_moods)

    @app.route("/all_moods")
    @login_required
    def all_moods():
        #  TODO Provide statistics on user compared to others and add to the render template
        return render_template("all_moods.html")

    
    # Handling logins, logouts, and registering users
    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Forget any user_id sessions
        session.clear()
        if request.method == "POST":

            # Ensure password and username were submitted
            if not request.form.get('username'):
                return apology("Must provide username", 403)
            if not request.form.get('password'):
                return apology("Must provide password", 403);
        
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")) or not len(request.form.get("username")) < 15:
                return apology("Invalid username and/or password!", 403)
            
            session["user_id"] = rows[0]["id"]
            flash("Logged in successfully.")
            return redirect("/")
        # USer reached the route via post
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        illegal_chars = "()=*-\\\'\".;:/\{\}#"
        """Register user"""
        # If user registers VIA POST
        if request.method == "POST":
            username, password, confirmation = request.form.get(
                "username"), request.form.get("password"), request.form.get("confirmation")
             # Only allow certain characters for username, sanitize user input
            for i in illegal_chars:
                for c in username:
                    if i == c:
                        return apology(f"These Characters are not allowed! {illegal_chars}")
            # Check if the password matches and if the user exits.
            if password == confirmation:
                user_exists = db.execute("SELECT * FROM users WHERE username = ?;", username)

                # Force users to have a password length longer than 8 characters and have at least 4 nonalphanumeric characters
                if len(password) < 8 and len(re.findall("\W+", password)) < 4:
                    return apology("Password must contain at least 8 characters and 4 nonalphanumeric character!")

                if len(user_exists) == 0:
                    # TODO had a new path for the user's image value, include all values in database. Start with the saddest color scheme
                    image_path = secrets.token_hex(16)
                    moodI(image_path, rgb=[57, 59, 87])
                    db.execute("INSERT INTO users (username, hash, path_to_img) VALUES(?, ?, ?)", username, generate_password_hash(password), image_path)
                    return redirect("/login")

                else:
                    return apology("User already exists!")

            else:
                return apology("Passwords do not match!")

        else:
            return render_template("register.html")
            
    
    return app

