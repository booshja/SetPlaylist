from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Favorite(db.Model):
    """
    Connection of a user <-> band
    """

    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    band_id = db.Column(db.Integer, db.ForeignKey("bands.id"))

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<Favorite user_id={self.user_id} band_id={self.band_id}>"


class User_Playlist(db.Model):
    """
    Connection of a user <-> playlist
    """

    __tablename__ = "users_playlists"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    band_id = db.Column(db.Integer, db.ForeignKey("bands.id"))

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<User_Playlist id={self.id} user_id={self.user_id} band_id={self.band_id}>"


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    secret_question = db.Column(db.Text, nullable=False)

    secret_answer = db.Column(db.Text, nullable=False)

    spotify_connected = db.Column(db.Boolean, nullable=False, default=None)

    spotify_user_token = db.Column(db.Text, default=None)

    spotify_user_id = db.Column(db.Text, default=None)

    favorites = db.relationship("Band", secondary="favorites")

    playlists = db.relationship(
        "Playlist", secondary="users_playlists", backref="users"
    )

    @classmethod
    def register(
        cls,
        username,
        password,
        secret_question,
        secret_answer,
        spotify_connected,
        spotify_user_token,
        spotify_user_id,
    ):
        """
        - Sign up user
        - Hash password and add user to system
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = cls(
            username=username,
            password=hashed_pwd,
            secret_question=secret_question,
            secret_answer=secret_answer,
            spotify_connected=spotify_connected,
            spotify_user_token=spotify_user_token,
            spotify_user_id=spotify_user_id,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        - Find user with username and password
        - If user - return user
        - If not user - return False
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False

    @classmethod
    def hash_password(password):
        """
        - Hash the given password
        - Return the hashed password
        """
        return bcrypt.generate_password_hash(password).decode("UTF-8")

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<User id={self.id} username={self.username} spotify_connected={self.spotify_connected}>"


class Playlist(db.Model):
    """
    Playlist Model
    """

    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True)

    spotify_playlist_id = db.Column(db.Text, nullable=False)

    name = db.Column(db.Text, nullable=False)

    description = db.Column(db.Text, nullable=False)

    tour_name = db.Column(db.Text, default=None)

    venue_name = db.Column(db.Text, default=None)

    event_date = db.Column(db.Text, default=None)

    venue_city = db.Column(db.Text, default=None)

    venue_state = db.Column(db.Text, default=None)

    length = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    band_id = db.Column(db.Integer, db.ForeignKey("bands.id"))

    songs = db.relationship("Song", secondary="playlists_songs", backref="playlists")

    band = db.relationship("Band")

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<Playlist id={self.id} name={self.name} description={self.description} length={self.length} user_id={self.user_id} band_id={self.band_id}>"


class Playlist_Song(db.Model):
    """
    Connection of a playlist <-> song
    """

    __tablename__ = "playlists_songs"

    id = db.Column(db.Integer, primary_key=True)

    playlist_id = db.Column(db.Integer, db.ForeignKey("playlists.id"))

    song_id = db.Column(db.Integer, db.ForeignKey("songs.id"))

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<Playlist_Song id={self.id} playlist_id={self.playlist_id} song_id={self.song_id}>"


class Band(db.Model):
    """
    Band Model
    """

    __tablename__ = "bands"

    id = db.Column(db.Integer, primary_key=True)

    spotify_artist_id = db.Column(db.Text, nullable=False)

    setlistfm_artist_id = db.Column(db.Text, nullable=False)

    name = db.Column(db.Text, nullable=False)

    bio = db.Column(db.Text)

    photo = db.Column(db.Text)

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<Band id={self.id} name={self.name}>"


class Song(db.Model):
    """
    Song Model
    """

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)

    spotify_song_id = db.Column(db.Text, nullable=False)

    spotify_song_uri = db.Column(db.Text, nullable=False)

    name = db.Column(db.Text, nullable=False)

    album_name = db.Column(db.Text, nullable=False)

    length = db.Column(db.Integer, nullable=False)

    band_id = db.Column(db.Integer, db.ForeignKey("bands.id"))

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<Song id={self.id} name={self.name} length={self.length} band_id={self.band_id}>"


def connect_db(app):
    """
    Connect database to Flask
    """
    db.app = app
    db.init_app(app)
