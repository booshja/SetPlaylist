# **README - SetPlaylist**

## **About**

_SetPlaylist_ ( Deployed [HERE](https://set-playlist.herokuapp.com/) ) is a web app that connects to your Spotify account and enables you to create playlists based off setlists of the artist's live performances. The artist's upcoming shows (if any) are also displayed on the artist's page.

---

## **Local Usage**

<br>

### **ENVs**:

This app uses the following environmental variables that you will need in order to run the app
| ENV | Value |
| --------------------- | --------------------------------------------------------- |
| `DATABASE_URI` | Postgres URI |
| `CURR_USER_KEY` | Value referencing the current user for session |
| `SECRET_KEY` | Flask secret key |
| `SETLIST_FM_API_KEY` | API Key from setlistfm |
| `SETLIST_FM_BASE_URL` | Base URL for setlistfm's API |
| `BIT_APP_ID` | Bandsintown API key |
| `BANDSINTOWN_BASE_URL` | Base URL for Bandsintown's API |
| `SPOTIFY_CLIENT_ID` | App-specific Client ID from Spotify's Developer Tools |
| `SPOTIFY_CLIENT_SECRET` | App-specific Client Secret from Spotify's Developer Tools |
| `SPOTIFY_BASE_URL` | Base URL for Spotify's web API |
| `SPOTIFY_REDIRECT_URI` | URL for spotify to redirect back to from user login |

<br>

### **Testing**:

In order to run the tests for this project locally, you will need to comment out the `DATABASE_URI` ENV so the app defaults to the testing database, as well as replace the following second block of code in `app.py` with the first. This app uses PostgreSQL databases, the testing db set up with the name `setplaylist_test`

<br>

### **Heroku Deployment Changes**:

In order to deploy through Heroku and use their PostgreSQL connection, this line of code:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URI', 'postgresql:///setplaylist_test')
```

Has been replaced with this:

```python
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
```

This deals with the issue of Heroku using the prefix "postgres:", whereas PostgreSQL has stopped supporting this prefix, now only using "postgresql:" exclusively.

<br>

### **Formatting/Linting/Pre-Commit Hooks**:

This project uses pre-commit hooks with isort, black, and flake8

<br>

### **Features**:

**Setlist Search**: In order to be able to find the setlist you'd like as a playlist, you need to search for it. The original plan (and long-term goal) was to allow users to search through all the artist's setlists with filtering functionality, but time constraints did not allow for this in its inital release form, and will be updated later on at some point. At this time, the artist's most recent 20 (or less) are displayed.

**Spotify Connection**: This allows the app to create a playlist and add songs to it within your Spotify account. This is an integral part of the idea of this app. Long-term goals include managing playlists- seeing the user's total list of playlists, ability to edit/delete them as well.

**Upcoming Shows**: This app features an artist's upcoming shows listed on their band display page. This feature was implemented because live shows are a centerpiece of this app, so upcoming shows are something the user would like to know.

<br>

### **APIs**:

1. [Setlist.fm API](https://api.setlist.fm/docs/1.0/index.html)
    > - Setlists from a band search results
    > - Specific setlist data
2. [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
    > - Band search results
    > - Account authorization:
    >     - Create/edit playlists
    >     - User's spotify ID
    > - Creating a new playlist and adding songs to it
    > - Band and Song Metadata
3. [Bandsintown API](https://app.swaggerhub.com/apis-docs/Bandsintown/PublicAPI/3.0.1)
    > - Upcoming shows for artist

<br>

### **Tech Stack**:

-   HTML
    -   [Jinja](https://jinja.palletsprojects.com/en/2.11.x/)
-   CSS
    -   [SASS](https://sass-lang.com/)
-   JavaScript
-   Python
    -   [WTForms](https://wtforms.readthedocs.io/en/2.3.x/)
    -   [Tekore](https://tekore.readthedocs.io/en/stable/index.html) - Python Wrapper For Spotify
    -   Unittest
-   Flask
    -   SQLAlchemy
    -   [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/)
-   PostgreSQL
-   [Heroku](https://heroku.com/)
-   VSCode
-   Caffeine

---

## **Support**

Reach out to me at the following places:

-   Website: [jacobandes.dev](jacobandes.dev)
-   Twitter: [@booshja](https://twitter.com/booshja)
-   Email: [jacob.andes@gmail.com](mailto:jacob.andes@gmail.com)

---

Copyright &#169; [Jacob Andes](jacobandes.dev), 2021
