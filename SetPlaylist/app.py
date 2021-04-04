import os

import requests
import spotipy
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session
from flask_debugtoolbar import DebugToolbarExtension
from forms import (
    ForgotPassAnswer,
    ForgotPassUsername,
    LoginForm,
    PasswordReset,
    RegisterForm,
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
from custom_cache import CustomCache
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
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

# toolbar = DebugToolbarExtension(app)

connect_db(app)

##################
# Global Methods ######################
##################


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
        del session["token"]


##############################
# User Login/Logout/Register ##########
##############################


@app.before_request
def add_to_g():
    """
    If user logged in, add to Flask global
    """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session(CURR_USER_KEY))
        g.cache_handler = CustomCache()
        g.auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=g.cache_handler)
        if g.auth_manager.validate_token(g.cache_handler.get_cached_token()):
            g.spotify = spotipy.Spotify(auth_manager=g.auth_manager)
    else:
        g.user = None
        g.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
                client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
            )
        )


@app.route("/register", methods=["POST"])
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
        # POST ROUTE FOR REGISTRATION FORM
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                secret_question=form.secret_question.data,
                secret_answer=form.secret_answer.data,
                spotify_connected=False,
                spotify_user_id=None,
            )
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username not available")
            return render_template(
                "auth.html", form=form, title="Register", q_display=""
            )

        session_login(user)

        return redirect("/home")

    # Spotify authorization flow
    g.cache_handler = CustomCache()
    auth_manager = SpotifyOAuth(
        client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI"),
        scope=os.environ.get("SPOTIPY_SCOPE"),
    )

    # If redirect back from Spotify
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect("/home")

    # Send user to login with Spotify
    if not auth_manager.validate_token(g.cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    g.spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect("/home")


@app.route("/register", methods=["GET"])
def show_registration_form():
    """
    GET ROUTE:
    - Show registration form
    """
    form = RegisterForm()
    return render_template("auth.html", form=form, title="Register", q_display="")


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

    return render_template("auth.html", form=form, title="Login", q_display="")


@app.route("/logout", methods=["POST"])
def logout():
    """
    POST ROUTE:
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
            return render_template(
                "auth.html", title="Forgot Password", form=form, q_display=""
            )

        session["password_reset"] = True
        return redirect(f"/forgot/{user.id}")

    return render_template(
        "auth.html", title="Forgot Password", form=form, q_display=""
    )


@app.route("/forgot/<int:user_id>", methods=["GET", "POST"])
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

    if not session.get("password_reset"):
        flash("Access Unauthorized")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        if User.authenticate_secret_answer(user.username, form.secret_answer.data):
            return redirect("/forgot/<user_id>/new")
        else:
            form.secret_answer.errors.append("Invalid secret answer")

    form.secret_question.data = user.secret_question

    return render_template(
        "/auth.html", form=form, title="Forgot Password", q_display="q_display"
    )


@app.route("/forgot/<int:user_id>/new", methods=["GET", "POST"])
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

    if not session.get("password_reset"):
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

    return render_template("auth.html", form=form, title="Reset Password", q_display="")


################
# Landing Page ########################
################


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


###############
# User Routes #########################
###############


@app.route("/user/home")
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
        return render_template("/user/home.html", recent_playlists=recent_playlists)


@app.route("/user/<int:user_id>/edit", methods=["GET", "POST"])
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
        if not form.secret_question and not form.secret_question:
            form.secret_question.errors.append(
                "Must change both secret question and answer together"
            )
            form.secret_answer.errors.append(
                "Must change both secret question and answer together"
            )
            return redirect(f"/user/{user_id}/edit")

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

    return render_template("/user/edit.html", form=form, title="Edit User")


###############
# Band Routes #########################
###############


@app.route("/band/<band_name>")
def show_band_details(band_name):
    """
    Todo - Shows band details
    """
    band = Band.query.filter_by(name=band_name).first()

    if band is None:
        url = os.environ.get("SETLIST_FM_BASE_URL") + "/search/artists"
        res = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "x-api-key": os.environ.get("SETLIST_FM_API_KEY"),
            },
            params=[("artistName", band_name)],
        ).json()

        fm_band = res["artists"][0]

        # TODO: Fix Spotify
        # Can't use spotify.artist, this requires a band uri or url, not a band name
        sp_band = g.spotify.artist(fm_band.name)

        search_name = Band.prep_band_name(fm_band.name)

        url = (
            os.environ.get("BANDSINTOWN_BASE_URL")
            + "/artists"
            + search_name
            + "/events"
        )
        upcoming_shows = requests.get()

    return render_template(
        "/band/search.html", band=sp_band, upcoming_shows=upcoming_shows
    )

    # If logged in - band, setlists, upcoming_shows
    # If not - band


@app.route("/band/<int:band_id>/setlist/<offset>")
def return_band_setlists_paginate(band_id, offset):
    """
    Todo - Shows further results for setlist results
            - Comes from JS axios call
    """
    # Do I need this? Could just pass entire list and have JS paginate


@app.route("/band/<int:band_id>/shows/<offset>")
def return_band_shows_paginate(band_id, offset):
    """
    Todo - Shows further results for show results
            -Comes from JS axios call
    """
    # Do I need this? Could just pass entire list and have JS paginate


######################
# Band Search Routes ##################
######################


@app.route("/band/search")
def search_page():
    """
    GET ROUTE:
    - Display search form
    """
    search = request.args.get("q")

    if not search:
        return render_template("band/search.html")
    else:
        url = os.environ.get("SETLIST_FM_BASE_URL") + "/search/artists"
        res = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "x-api-key": os.environ.get("SETLIST_FM_API_KEY"),
            },
            params=[("artistName", search)],
        ).json()

    return render_template(
        "/band/search.html", search=search, band_results=res["artist"]
    )


###################
# Playlist Routes #####################
###################


@app.route("/playlist/setlist")
def show_setlist():
    """
    Todo - Shows the setlist data that was selected
    """
    # setlist (Playlist object that has not been saved to the db)


@app.route("/playlist/<int:playlist_id>")
def show_created_playlist():
    """
    Todo - Shows the setlist that was created
    """
    # playlist (Playlist object saved to db)


@app.route("/playlist/<int:band_id>/hype")
def show_hype_setlist():
    """
    Todo - Shows the setlist created from band's top songs
    """
    # playlist (Playlist object saved to db, created from band's top songs from spotify)


@app.route("/playlist/success")
def show_success_page():
    """
    Todo - shows the success page after playlist saved to spotify
    """
    # spotify_link (link to open playlist via spotify)


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
    return render_template("/errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("/errors/500.html"), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template("/errors/403.html"), 403
