import unittest
import logging
from datetime import datetime

from common import scrapers
from common.players import spotify
from common.players.spotify import SpotifyPlayer

import os, sys
sys.path.insert(0, os.path.abspath('..'))

class TestSpotifyPlayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.spotify = SpotifyPlayer('kkdoom')

    def tearDown(self):
        pass

    def test_get_track(self):
        test_track_info = {'artist': 'Courtney Barnett', 'track': 'Pedestrian at Best'}

        spfy_tracks = self.spotify.search_track(test_track_info)

        for track in spfy_tracks:
            logging.debug('retrived track {track}'.format(track=track))

        self.assertTrue(len(spfy_tracks) > 0)

    def test_create_playlist(self):
        test_description = 'test description for test playlist 1234'
        username = 'kkdoom'
        #create test playlist
        self.spotify.create_playlist('test_playlist', test_description)

        #verify the playlist was added
        playlists = self.spotify.auth_spotipy.user_playlists(username)

        found_playlist = False

        for playlist in playlists['items']:
            if playlist['owner']['id'] == username and playlist['name'] == 'test_playlist':
                found_playlist = True

        print('No spotify api exists to remove playlist, so remember to delete test_playist on your profile!')

        self.assertTrue(found_playlist)


    def test_add_track_to_playlist(self):
        pass


