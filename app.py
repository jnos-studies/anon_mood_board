import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

from free_apis import get_random_quote as quote

from authentication import apology, login_required

from datetime import datetime as date

import re

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
Session(app)

db = SQL("sqlite:///test_data.db")
