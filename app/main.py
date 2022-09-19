import os
import secrets
# TODO implement request limiter before publishing!
# https://medium.com/analytics-vidhya/how-to-rate-limit-routes-in-flask-61c6c791961b
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from authentication import login_required, apology, convert_to_regexp
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

    #configure session to use file-system (instead of signed cookies)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["DEBUG"] = True
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
        # Reverse list object to put most recently logged on top
        reverse_moods = []
        for m in moods:
            reverse_moods.insert(0, m)
        
        # Get a quote to put on user's homepage
        inspirational_quote = quote()

        return render_template("index.html", image_path=user_image_path, username=username[0]["username"], moods=reverse_moods, rgb=config.RGB_SCHEME_MAP, quote_text=inspirational_quote['text'], quote_author=inspirational_quote['author'])

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
                # Get selected rating
                rating = request.form["inlineRadioOptions"]

                # Get the one word description after validating that it is one word and purely alphabetic
                emot_description = request.form.get("emot_description")
                r_pattern = convert_to_regexp(emot_description)
                # If there is a space, digit or the escape character '\' it is an invalid input
                regex = re.search("[\d\s\\\]", r_pattern)
                if regex:
                    flash("Only single word descriptions of your mood are allowed!")
                    return redirect("/log_mood")
                
                # Otherwise insert logged mood into moods
                db.execute("INSERT INTO moods(user_id, rating) VALUES(?, ?)", session["user_id"], rating)
                # id of the last mood the user has logged
                mood_id = db.execute("SELECT * FROM moods WHERE user_id = ?", session["user_id"])[-1:][0]["mood_id"]
                # insert into the moods descriptions table
                db.execute("INSERT INTO mood_descriptions(fmood_id, description) VALUES(?, ?)", mood_id, emot_description)
                
                average_feels = int(db.execute("SELECT avg(rating) AS average FROM moods WHERE user_id = ?", session["user_id"])[0]["average"])
                moodI(user_image_path, rgb=config.RGB_SCHEME_MAP[average_feels])

                return redirect("log_mood")


        return render_template("log_mood.html", log_nums=num_logged_moods)

    @app.route("/all_moods")
    @login_required
    def all_moods():
        # Show the most rated feelings that the user has selected
        user_most_rated = db.execute("SELECT rating, COUNT(*) AS count FROM moods WHERE user_id = ? GROUP BY rating;", session["user_id"])
        user_rate = [r["rating"] for r in user_most_rated]
        user_rate_count = [r["count"] for r in user_most_rated]
        all_users_most_rated = db.execute("SELECT rating, COUNT(*) AS count FROM moods WHERE rating in (SELECT DISTINCT rating FROM moods WHERE user_id = ?) GROUP BY rating;", session["user_id"])
        all_users_rate = [r["rating"] for r in all_users_most_rated]
        all_users_rate_count = [r["count"] for r in all_users_most_rated]

        daily_avg_user = db.execute("SELECT strftime('%m-%d-%Y', date) AS fdate, COUNT(*) AS count, AVG(rating) as average_rating FROM moods WHERE user_id = ? GROUP BY fdate;", session["user_id"])
        dau_x = [a["fdate"] for a in daily_avg_user]
        dau_y = [a["average_rating"] for a in daily_avg_user]

        daily_avg_all = db.execute("SELECT * FROM daily_average WHERE fdate IN (SELECT strftime('%m-%d-%Y', date) AS fdate FROM moods WHERE user_id = ? GROUP BY fdate)", session["user_id"])

        daa_x = [a["fdate"] for a in daily_avg_all if a["fdate"]]
        daa_y = [a["average_rating"] for a in daily_avg_all]

        return render_template("all_moods.html",\
            user_rated=user_rate, user_rated_count=user_rate_count,\
            all_rated=all_users_rate, all_rated_count=all_users_rate_count,\
            user_daily_x=dau_x, daily_avg_all_x=daa_x,\
            user_daily_y=dau_y, daily_avg_all_y=daa_y)

    
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
             # TODO implement this with sre_parse module instead
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

