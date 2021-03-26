from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
# from sqlalchemy.exc import
# from forms import
from models import db, connect_db, User

load_dotenv()

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URI', 'postgres:///setplaylist-test')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret!')

CURR_USER_KEY = os.environ.get('CURR_USER_KEY')

toolbar = DebugToolbarExtension(app)

connect_db(app)

################################################################################


@app.before_request
def add_user_to_g():
    """
    If user logged in, add to Flask global
    """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None
