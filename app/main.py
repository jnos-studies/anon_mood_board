import os
import secrets
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from authentication import login_required, apology
from datetime import datetime as date

import re

def create_app(testing: bool = True):

    app = Flask(__name__)
    # configure session to use filesystem (instead of signed cookies)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SECRET_KEY"] = secrets.token_hex(16)
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
        return render_template("index.html")

    @app.route("/log_mood")
    @login_required
    def log_mood():
        return render_template("log_mood.html")

    @app.route("/all_moods")
    @login_required
    def all_moods():
        return render_template("all_moods.html")

    
    # Handling logins, logouts, and registering users
    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Forget any user_id sessions
        if len(session) > 0:
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
        redirect("/")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            pass
        return render_template("register.html")

    
    return app