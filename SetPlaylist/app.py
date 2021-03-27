import os
import re

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session
from flask_debugtoolbar import DebugToolbarExtension
from forms import (
    ForgotPassAnswer,
    ForgotPassUsername,
    LoginForm,
    PasswordReset,
    RegisterForm,
    SearchForm,
    UserEditForm,
)
from models import User, connect_db, db
from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", "postgres:///setplaylist-test"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret!")

CURR_USER_KEY = os.environ.get("CURR_USER_KEY")

toolbar = DebugToolbarExtension(app)

connect_db(app)

################################################################################
# User Login/Logout/Register


@app.before_request
def add_user_to_g():
    """
    If user logged in, add to Flask global
    """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def session_login(user):
    """
    Login user to Flask session
    """
    session[CURR_USER_KEY] = user.id


def session_logout(user):
    """
    Logout user from Flask session
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET ROUTE:
    - Display register form
    --------------------
    POST ROUTE:
    Handle user registration
    - Create new user and add to DB
    - Redirect to Landing Page
    - If form not valid, present form
    - If username in user
        - Flash message and re-present form
    """

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                secret_question=form.secret_question.data,
                secret_answer=form.secret_answer.data,
            )
            db.session.commit()
        except IntegrityError:
            flash("Username not available", "error")
            return render_template("register.html", form=form)

        session_login(user)

        return redirect("/home")
    else:
        return render_template("register-edit.html", form=form, title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET ROUTE:
    - Display login form
    --------------------
    POST ROUTE:
    - Handle user login
    """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session_login(user)
            return redirect("/")
        flash("Invalid username/password", "error")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """
    GET ROUTE:
    - Handle logout of user
    """
    session_logout()
    return redirect("/")


################################################################################


@app.route("/")
def landing():
    """
    GET ROUTE:
    -
    """
    if g.user:
        return redirect("/home")
    else:
        return render_template("landing.html")


@app.route("/home")
def homepage():
    """
    GET ROUTE:
    -
    """
    if not g.user:
        return redirect("/")
    else:
        return render_template("home.html")


################################################################################


@app.route("/user/<user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """
    GET ROUTE:
    - Displays User Edit Form
    --------------------
    POST ROUTE:
    - Checks password
    - If passes
        - Updates any data changed
        - Commits changes to database
        - Redirects to User Homepage
    """
    form = UserEditForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        user = User.query.get_or_404(user_id)

        if User.authenticate(user.username, current_password):
            user.username = form.username.data or user.username
            user.email = form.email.data or user.email
            user.secret_question = form.secret_question.data or user.secret_question
            user.secret_answer = form.secret_answer.data or user.secret_answer

            new_password = form.new_password.data or None
            retype_password = form.retype_password.data or None
            if (
                new_password is not None
                and retype_password is not None
                and new_password == retype_password
            ):
                user.password = User.hash_password(new_password)

            try:
                db.add(user)
                db.commit()
            except IntegrityError:
                flash("Username taken", "error")
                return redirect(f"/user/{user_id}/edit")

            return redirect("/home")
        else:
            flash("Incorrect Password", "error")

    return redirect(f"/user/{user_id}/edit", form=form)
