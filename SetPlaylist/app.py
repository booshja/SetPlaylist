import os
import re

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, requests, session
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
from models import (
    Band,
    Favorite,
    Playlist,
    Playlist_Song,
    Song,
    User,
    User_Playlist,
    connect_db,
    db,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

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

##############################
# User Login/Logout/Register ##########
##############################


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
        - Add username error message and re-present form
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
            form.username.errors.append("Username not available")
            return render_template("register.html", form=form, title="Register")

        session_login(user)

        return redirect("/home")
    else:
        return render_template("register.html", form=form, title="Register")


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
        form.username.errors.append("Invalid username/password")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """
    GET ROUTE:
    - Handle logout of user
    """
    session_logout()
    return redirect("/")


#########################
# Reset Password Routes ###############
#########################


@app.route("/forgot", methods=["GET", "POST"])
def forgot_password_check_username():
    """
    GET ROUTE:
    - Display form for username entry for forgotten password
    --------------------
    POST ROUTE:
    - Checks that username is in database
    - If username is in database
        - Redirects to next page
    - If username not in database
        - Display error, redisplay form
    """
    form = ForgotPassUsername()

    if g.user:
        flash("You can change your password here")
        return redirect(f"/user/{g.user.id}/edit")

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).one()
        except NoResultFound or MultipleResultsFound:
            form.username.errors.append("Username not found")
            return render_template("password.html", title="Forgot Password", form=form)

        g.password_reset = True
        return redirect(f"/forgot/{user.id}")

    return render_template("password.html", title="Forgot Password", form=form)


@app.route("/forgot/<user_id>", methods=["GET", "POST"])
def forgot_password_check_secret_question(user_id):
    """
    GET ROUTE:
    - Display form for secret question/answer
    --------------------
    POST ROUTE:
    - Check the secret answer
    - Redirect to '/forgot/<user_id>/new'
    """
    form = ForgotPassAnswer()

    if not g.password_reset:
        flash("Access Unauthorized")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        if User.authenticate_secret_answer(user.username, form.secret_answer.data):
            return redirect("/forgot/<user_id>/new")
        else:
            form.secret_answer.errors.append("Invalid secret answer")

    form.secret_question.data = user.secret_question

    return render_template("password.html", form=form, title="Forgot Password")


@app.route("/forgot/<user_id>/new", methods=["GET", "POST"])
def forgot_password_new_password(user_id):
    """
    GET ROUTE:
    - Display form for password reset
    --------------------
    POST ROUTE:
    - Check that password fields match
    - Save change to database
    - Redirect to login page
    """
    form = PasswordReset()

    if not g.password_reset:
        flash("Access Unauthorized")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        if form.new_password.data == form.retype_password.data:
            hashed_pwd = User.hash_password(form.new_password.data)
            user.password = hashed_pwd

            db.add(user)
            db.commit()

            g.password_reset = False

            return redirect("/login")
        else:
            form.new_password.errors.append("Passwords must match")
            return render_template("password.html", title="Reset Password", form=form)

    return render_template("password.html", form=form, title="Reset Password")


##########################
# Landing and Home Pages ##############
##########################


@app.route("/")
def landing():
    """
    GET ROUTE:
    - If user logged in, redirect to '/home'
    - If logged out, return logged out landing page
    """
    if g.user:
        return redirect("/home")
    else:
        return render_template("landing.html")


@app.route("/home")
def homepage():
    """
    GET ROUTE:
    - If user logged out, redirect to '/'
    - If logged in, return logged in homepage
    """
    if not g.user:
        return redirect("/")
    else:
        recent_playlists = Playlist.query.order_by(Playlist.id.desc()).limit(10)
        return render_template("home.html", recent_playlists=recent_playlists)


#################
# Search Routes #######################
#################


@app.route("/search")
def search_page():
    """
    GET ROUTE:
    - Display search form
    """
    return render_template("search.html")


@app.route("/search/<q>")
def search_results(q):
    """
    GET ROUTE:
    - Call Setlist.fm API for search
    - Display search results
    """
    url = os.environ.get("SETLIST_FM_BASE_URL") + "/search/artists"
    band_results = requests.get(
        url,
        headers={
            "Accept": "application/json",
            "x-api-key": os.environ.get("SETLIST_FM_API_KEY"),
        },
        params=[("artistName", q)],
    )
    return render_template("search.html", q=q, band_results=band_results)


###############
# User Routes #########################
###############


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
                form.username.errors.append("Username unavailable")
                return redirect(f"/user/{user_id}/edit")

            return redirect("/home")
        else:
            form.password.errors.append("Incorrect Password")

    return render_template("edit.html", form=form, title="Edit User")


###############
# Band Routes #########################
###############


@app.route("/band/<band_id>")
def show_band_details(band_id):
    """
    Todo - Shows band details
    """


@app.route("/band/<band_id>/setlist/<offset>")
def return_band_setlists_paginate(band_id, offset):
    """
    Todo - Shows further results for setlist results
            - Comes from JS axios call
    """


@app.route("/band/<band_id>/shows/<offset>")
def return_band_shows_paginate(band_id, offset):
    """
    Todo - Shows further results for show results
            -Comes from JS axios call
    """


###################
# Playlist Routes #####################
###################


@app.route("/playlist/setlist")
def show_setlist():
    """
    Todo - Shows the setlist data that was selected
    """


@app.route("/playlist/<playlist_id>")
def show_created_setlist():
    """
    Todo - Shows the setlist that was created
    """


@app.route("/playlist/<band_id>/hype")
def show_hype_setlist():
    """
    Todo - Shows the setlist created from band's top songs
    """


@app.route("/playlist/success")
def show_success_page():
    """
    Todo - shows the success page after playlist saved to spotify
    """


@app.route("/playlist/failure")
def show_failure_page():
    """
    Todo - shows the failure page after playlist not saved to spotify
    """


#######################
# Custom Error Routes #################
#######################


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403
