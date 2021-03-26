from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

# TODO: Add relationships
# TODO: Add joins


class User(db.Model):
    """
    User Model
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    secret_question = db.Column(db.Text, nullable=False)

    secret_answer = db.Column(db.Text, nullable=False)

    spotify_connected = db.Column(db.Boolean, nullable=False)

    spotify_user_token = db.Column(db.Text, default=None)

    spotify_user_id = db.Column(db.Text, default=None)

    def __repr__(self):
        """
        A more readable representation of the instance
        """
        return f"<User id={self.id} username={self.username} spotify_connected={self.spotify_connected}>"

    @classmethod
    def register(cls, username, password, secret_question, secret_answer, spotify_connected, spotify_user_token, spotify_user_id):
        """
        - Sign up user
        - Hash password and add user to system
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, password=hashed_pwd, secret_question=secret_question, secret_answer=secret_answer,
                    spotify_connected=spotify_connected, spotify_user_token=spotify_user_token, spotify_user_id=spotify_user_id)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        - Find user with username and password
        - If user - return user
        - If !user - return False
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class Playlist(db.Model):
    """
    Playlist Model
    """

    __tablename__ = 'playlists'

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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'))


class Band(db.Model):
    """
    Band Model
    """

    __tablename__ = 'bands'

    id = db.Column(db.Integer, primary_key=True)

    spotify_artist_id = db.Column(db.Text, nullable=False)

    setlistfm_artist_id = db.Column(db.Text, nullable=False)

    name = db.Column(db.Text, nullable=False)

    bio = db.Column(db.Text)

    photo = db.Column(db.Text)


class Song(db.Model):
    """
    Song Model
    """

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)

    spotify_song_id = db.Column(db.Text, nullable=False)

    spotify_song_uri = db.Column(db.Text, nullable=False)

    name = db.Column(db.Text, nullable=False)

    album_name = db.Column(db.Text, nullable=False)

    length = db.Column(db.Integer, nullable=False)

    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'))


def connect_db(app):
    """
    Connect database to Flask
    """
    db.app = app
    db.init_app(app)
