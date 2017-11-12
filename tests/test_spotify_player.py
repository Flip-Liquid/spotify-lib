import unittest
import logging
from datetime import datetime

from common import scrapers
from common.players import spotify
from common.players.spotify import SpotifyPlayer

import json

import os, sys
sys.path.insert(0, os.path.abspath('..'))

class TestSpotifyPlayer(unittest.TestCase):
    test_dir = "test_cases"

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

        dir_path = os.path.dirname(os.path.realpath(__file__))
        test_case = os.path.join(dir_path, self.test_dir, "test_get_track.json")

        with open(test_case) as f:

            test_json = json.loads(f.read())

            for test in test_json:

                logging.debug(test["_comment"])

                test_track_info = test["track_info"]
                test_expected_id = test["expected_ids"]

                for track_info in test_track_info:

                    spfy_tracks = self.spotify.search_track(track_info)

                    for track in spfy_tracks:
                        logging.debug("retrived track {track}".format(track=track))

                    test_id = track_info["test_id"]
                    retrieved_track_id = spfy_tracks['tracks']['items'][0]['id']
                    expected_spotify_id = test_expected_id['test_id'][str(test_id)]['spotify_id']
                    self.assertEqual(expected_spotify_id, retrieved_track_id)


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
        track = {'artist': 'Massive Attack', 'track' : 'Be Thankful For What You\'ve Got'}

        self.spotify.search_track(track)

        playlist_id = self.spotify.create_playlist('one luv bruv')

        self.spotify.add_tracks_to_playlist_by_name([track], playlist_id)

