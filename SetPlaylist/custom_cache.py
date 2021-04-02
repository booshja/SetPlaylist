from spotipy import CacheHandler
from flask import session


class CustomCache(CacheHandler):
    """
    Custom Cache Handler for spotipy
    """

    def get_cached_token(self):
        """
        Get and return a token_info dictionary object
        """

        if not session.get("token"):
            return None
        else:
            return session.get("token")

    def save_token_to_cache(self, token_info):
        """
        Save a token_info dictionary object to the cache and return None
        """
        session["token"] = token_info
        return None
