import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from free_apis import get_random_quote as quote
from image_generator import make_mood_image
from authentication import apology, login_required

from datetime import datetime as date

import re

app = Flask(__name__)

# configure session to use filesystem (instead of signed cookies)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
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

@app.route("/")
@login_required
def index():
    """Show user's homepage"""