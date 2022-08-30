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
        return response
    # User home page will show them how many times they logged their mood,
    # There generated mood color, how many users share similar moods,
    # And others
    @app.route("/")
    @login_required
    def index():
        # Get user's mood image to display
        user_image_path = "static/mood_images/" + db.execute("SELECT path_to_img FROM users WHERE id = ?", session["user_id"])[0]["path_to_img"] + ".png"
        return render_template("index.html", image_path=user_image_path)

    @app.route("/log_mood")
    @login_required
    def log_mood():
        return render_template("log_mood.html")

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
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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

