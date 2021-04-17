from unittest import TestCase

from app import app
from models import Band, Playlist, Song, User, db

db.create_all()


class UserModelTestCase(TestCase):
    """
    Test models for users
    """

    def setUp(self):
        """
        Clean up data
        """
        User.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        Band.query.delete()

    def tearDown(self):
        """
        Clean up any failed transactions
        """
        db.session.rollback()

    def test_user_model(self):
        """
        TESTS:
        - Basic model works
        """
        u = User(
            username="john_doe",
            password="password",
            email="test@email.com",
            secret_question="What's the magic word?",
            secret_answer="Banana",
        )
        db.session.add(u)
        db.session.commit()

        self.assertGreaterEqual(u.id, 1)
        self.assertEqual(u.spotify_user_id, None)
        self.assertEqual(u.spotify_user_id, None)

    def test_repr_method(self):
        """
        TESTS:
        - Repr method works as expected
        """
        u = User(
            username="john_doe",
            password="password",
            email="test@email.com",
            secret_question="What's the magic word?",
            secret_answer="Banana",
        )
        db.session.add(u)
        db.session.commit()
        db_user = User.query.filter_by(username="john_doe").first()

        self.assertEqual(
            str(db_user),
            f"<User id={db_user.id} username={db_user.username} email={db_user.email}>",
        )

    def test_user_signup_success(self):
        """
        TESTS:
        - User.register successfully create a new user given valid credentials?
        """
        u = User.register(
            username="john_doe",
            password="password",
            email="test@email.com",
            secret_question="What's the magic word?",
            secret_answer="Banana",
        )
        db.session.add(u)
        db.session.commit()
        db_user = User.query.filter_by(username="john_doe").first()

        self.assertEqual(db_user.username, "john_doe")
        self.assertEqual(db_user.email, "test@email.com")
        self.assertNotEqual(db_user.password, "password")
        self.assertNotEqual(db_user.secret_answer, "Banana")

    def test_authentication(self):
        """
        TESTS:
        - User.authenticate successfully return a user when given a valid username and password?
        - User.authenticate fail to return a user when the username is invalid?
        """
        u = User.register(
            username="john_doe",
            password="password",
            email="test@email.com",
            secret_question="What's the magic word?",
            secret_answer="Banana",
        )
        db.session.commit()
        db_user = User.query.filter_by(username="john_doe").first()

        self.assertEqual(
            User.authenticate(username=db_user.username, password="password"), u
        )
        self.assertEqual(User.authenticate(username="bob", password="password"), False)

    def test_secret_answer_authentication(self):
        """
        TESTS:
        - User.authenticate_secret_answer successfully return True when given a valid secret answer?
        - User.authenticate_secret_answer return False when the secret answer is invalid?
        """
        u = User.register(
            username="john_doe",
            password="password",
            email="test@email.com",
            secret_question="What's the magic word?",
            secret_answer="Banana",
        )
        db.session.add(u)
        db.session.commit()
        db_user = User.query.filter_by(username="john_doe").first()

        self.assertEqual(
            User.authenticate_secret_answer(username=db_user.username, answer="Banana"),
            True,
        )
        self.assertEqual(
            User.authenticate_secret_answer(username=db_user.username, answer="secret"),
            False,
        )


class PlaylistModelTestCase(TestCase):
    """
    Test model for playlists
    """

    def setUp(self):
        """
        Clean up data
        """
        User.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        Band.query.delete()

        band = Band(
            spotify_artist_id="THE artist",
            setlistfm_artist_id="the ONLY artist",
            name="The Only Band In The Database",
            photo="No thanks",
        )
        db.session.add(band)
        db.session.commit()
        db_band = Band.query.filter_by(name="The Only Band In The Database").first()

        p = Playlist(
            setlistfm_setlist_id="setlistfmid",
            name="This is a playlist",
            description="The name says it all",
            tour_name="Testing World Tour 2021",
            venue_name="My desk at home",
            event_date="The Pandemic",
            venue_loc="Working from home",
            length=99,
            duration="The rest of time",
            band_id=db_band.id,
        )
        db.session.add(p)
        db.session.commit()

    def tearDown(self):
        """
        Clean up any failed transactions
        """
        db.session.rollback()

    def test_playlist_model(self):
        """
        TESTS:
        - Basic model works
        """
        db_playlist = Playlist.query.filter_by(
            setlistfm_setlist_id="setlistfmid"
        ).first()

        self.assertGreaterEqual(db_playlist.id, 1)
        self.assertEqual(db_playlist.spotify_playlist_id, "pending")
        self.assertEqual(db_playlist.tour_name, "Testing World Tour 2021")

    def test_repr_model(self):
        """
        TESTS:
        - Repr method works as expected
        """
        db_playlist = Playlist.query.filter_by(
            setlistfm_setlist_id="setlistfmid"
        ).first()

        self.assertEqual(
            str(db_playlist),
            f"<Playlist id={db_playlist.id} name={db_playlist.name} description={db_playlist.description} length={db_playlist.length} band_id={db_playlist.band_id}>",
        )

    def test_add_songs_method(self):
        """
        TESTS:
        - add_songs method works as expected
        """
        songs = ["Song 1", "Song 2"]
        p = Playlist(
            setlistfm_setlist_id="setlistfmid",
            name="This is a playlist",
            description="The name says it all",
            tour_name="Testing World Tour 2021",
            venue_name="My desk at home",
            event_date="The Pandemic",
            venue_loc="Working from home",
            length=99,
            duration="The rest of time",
        )
        p.add_songs(songs)

        self.assertEqual(p.songz, ["Song 1", "Song 2"])

    def test_format_duration(self):
        """
        TESTS:
        - format_duration method works as expected
        """
        db_playlist = Playlist.query.filter_by(
            setlistfm_setlist_id="setlistfmid"
        ).first()

        self.assertEqual(db_playlist.format_duration(6225), "1hrs. 43min. 45sec.")


class BandModelTestCase(TestCase):
    """
    Test model for bands
    """

    def setUp(self):
        """
        Clean up data
        """
        User.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        Band.query.delete()

    def tearDown(self):
        """
        Clean up any failed transactions
        """
        db.session.rollback()

    def test_band_model(self):
        """
        TESTS:
        - Basic model works
        """
        b = Band(
            spotify_artist_id="spotifyID",
            setlistfm_artist_id="anotherID",
            name="The Only Band In Teh Database",
            photo="Unphotographable",
        )
        db.session.add(b)
        db.session.commit()
        db_band = Band.query.filter_by(photo="Unphotographable").first()

        self.assertGreaterEqual(db_band.id, 1)
        self.assertEqual(db_band.spotify_artist_id, "spotifyID")
        self.assertEqual(db_band.name, "The Only Band In Teh Database")

    def test_repr_method(self):
        """
        TESTS:
        - Repr method works as expected
        """
        b = Band(
            spotify_artist_id="spotifyID",
            setlistfm_artist_id="anotherID",
            name="The Only Band In Teh Database",
            photo="Unphotographable",
        )
        db.session.add(b)
        db.session.commit()
        db_band = Band.query.filter_by(photo="Unphotographable").first()

        self.assertEqual(str(db_band), f"<Band id={db_band.id} name={db_band.name}>")

    def test_bit_prep_band_name(self):
        """
        TESTS:
        - bit_prep_band_name method works as expected
        """
        name = 'test test/test?test*test"test'
        formatted = Band.bit_prep_band_name(name)

        self.assertEqual(formatted, "test%20test%252Ftest%253Ftest%252Atest%27Ctest")


class SongModelTestCase(TestCase):
    """
    Test model for songs
    """

    def setUp(self):
        """
        Clean up data
        """
        User.query.delete()
        Song.query.delete()
        Playlist.query.delete()
        Band.query.delete()

        b = Band(
            spotify_artist_id="spotifyID",
            setlistfm_artist_id="anotherID",
            name="THE Band",
            photo="Not Today",
        )
        db.session.add(b)
        db.session.commit()

    def tearDown(self):
        """
        Clean up any failed transactions
        """
        db.session.rollback()

    def test_song_model(self):
        """
        TESTS:
        - Basic model works
        """
        db_band = Band.query.filter_by(name="THE Band").first()

        s = Song(
            spotify_song_id="YetAnotherID",
            name="The Greatest Song In The World",
            duration=900,
            band_id=db_band.id,
        )
        db.session.add(s)
        db.session.commit()
        db_song = Song.query.filter_by(name="The Greatest Song In The World").first()

        self.assertGreaterEqual(db_song.id, 1)
        self.assertEqual(db_song.spotify_song_id, "YetAnotherID")
        self.assertEqual(db_song.duration, 900)

    def test_repr_method(self):
        """
        TESTS:
        - Repr method works as expected
        """
        db_band = Band.query.filter_by(name="THE Band").first()

        s = Song(
            spotify_song_id="YetAnotherID",
            name="The Greatest Song In My World",
            duration=900,
            band_id=db_band.id,
        )
        db.session.add(s)
        db.session.commit()
        db_song = Song.query.filter_by(name="The Greatest Song In My World").first()

        self.assertEqual(
            str(db_song),
            f"<Song id={db_song.id} name={db_song.name} duration={db_song.duration} band_id={db_song.band_id}>",
        )
