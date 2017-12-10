#definition for api to create spotify playlist and check if track exists in service

import sys, os
sys.path.insert(0, os.path.abspath('..'))

import math
import logging

import spotipy
import spotipy.util

from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyPlayer(object):
    """
    Class for interacting with spotify. Relies on spotipy. Gets a token for a partiuclar
    user, and creates spotipy instance from this token for user operations.

    Uses client credential flow for getting and searching for track ids.
    """
    def __init__(self, spfy_user_id, spfy_app_id='', spfy_app_secret=''):
        """
        Constructor for the spotify player class

        :param spfy_app_id: id of the client application registered with spotify
        :param spfy_app_secret: secret of the client application registered with spotify
        :param sofy_user_id: user id who's playlists we want to change
        """
        playlist_write_scope = 'playlist-modify-public'

        client_credentials_manager = None
        auth_spotipy = None

        self.user_id=spfy_user_id

        #If client id & sceret specified, initialize with the supplied values. Otherwise, assume that they have been
        #set as environment variables
        if spfy_app_id != '' and spfy_app_secret != '':
            client_credentials_manager = SpotifyClientCredentials(spfy_app_id, spfy_app_secret)
            auth_spotipy = spotipy.Spotify(auth=spotipy.util.prompt_for_user_token(
                spfy_user_id, playlist_write_scope, spfy_app_id, spfy_app_secret))
        else:
            client_credentials_manager = SpotifyClientCredentials()
            auth_spotipy = spotipy.Spotify(auth=spotipy.util.prompt_for_user_token(spfy_user_id, playlist_write_scope))

        self.auth_spotipy = auth_spotipy
        self.ccm_spotipy = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def create_playlist(self, playlist_name, description=''):
        """
        Creates playlist with the specified name. Description is currently ignored.
        """
        logging.debug('creating playlist for user {user}: {playlist} --- {description}'.format(
            user=self.user_id, playlist=playlist_name, description=description))

        result = None

        try:
            result = self.auth_spotipy.user_playlist_create(self.user_id, playlist_name)
        except:
            e = sys.exc_info()[0]
            logging.error('error in creating playlist for user {user}: {playlist} --- {description}... error: {error}'.format(
                user=self.user_id, playlist=playlist_name, description=description, error=e))
            raise

        playlist_id = result['id']

        logging.debug('created playlist {name} with id {id}'.format(name=playlist_name, id=playlist_id))

        return playlist_id

    def add_track_ids_to_playlist(self, user_id, playlist_id, track_ids):
        """
        Add track ids to specified playlist (spotify can only add 100 at a time)
        Adds in batches of batch_size
        :param user_id: username of the user who owns the specified playlist
        :param playlist_id: playlist to which we're adding tracks
        :param track_ids: list of track ids that we're adding to playlist
        """
        batch_size = 75
        dedeuplicated_track_ids = []

        #Try to pre-populate track ids with whatever's already in the playlist
        if self.check_playlist_exists(user_id, playlist_id):
            dedeuplicated_track_ids = self.get_tracks_in_playlist(user_id, playlist_id)

        for i in track_ids:
            if i not in dedeuplicated_track_ids:
                dedeuplicated_track_ids.append(i)

        for i in range(0, math.ceil(len(dedeuplicated_track_ids) / batch_size)):
            #get current slize of track ids
            max_ind = min(len(dedeuplicated_track_ids), (i+1)*batch_size)
            logging.debug('Max_index: {}'.format(max_ind))
            track_id_slice = dedeuplicated_track_ids[i*batch_size:max_ind]

            logging.info('Attempting to add {} tracks'.format(len(track_id_slice)))

            try:
                self.auth_spotipy.user_playlist_add_tracks(user_id, playlist_id, track_id_slice)
            except:
                e = sys.exc_info()[0]
                logging.error('error in adding tracks {tracks} to playlist {playlist} for user {user} :{e}'.format(
                    tracks=track_id_slice, playlist=playlist_id, user=user_id, e=e))
                raise

    def get_tracks_in_playlist(self, user_id, playlist_id):
        track_ids = []

        playlist_tracks = self.auth_spotipy.user_playlist_tracks(user_id, playlist_id=playlist_id)
        track_ids = [playlist_track['track']['id'] for playlist_track in playlist_tracks['items']]

        return track_ids

    def add_tracks_to_playlist_by_name(self, user_id, playlist_id, track_info):
        """
        Adds a track to the specified playlist id using track_info as a best-guess

        :param track_info: A list of dictionaries containing either 'artist' and 'track' keys or a 'blob'
        :param playlist_id: spotify's numerical representation of a particular playlist
        """
        track_ids = self.get_track_ids_from_track_info(track_info)
        self.add_track_ids_to_playlist(user_id, playlist_id, track_ids)

    def get_playlist_id_from_name(self, user_id, playlist_name):
        """
        :param playlist_name: friendly name of the playlist
        :param user_id: user_id whose playlist we want
        """
        if user_id == '':
            user_id = self.user_id

        playlists = []

        try:
            playlists = self.auth_spotipy.user_playlists(user_id)
        except:
            e = sys.exc_info()[0]
            logging.error('error in getting playlist {playlist_name} for user {user}: {e}'.format(
                user=user_id, playlist_name=playlist_name, e=e))
            raise

        for playlist in playlists['items']:
            if playlist['owner']['id'] == user_id and playlist['name'] == playlist_name:
                return playlist['id']

        logging.warning('no playlist with name {name} found in {user}\'s account'.format(name=playlist_name,user=user_id))

        return None

    def check_playlist_exists(self, user_id, playlist_name):
        """
        :param user_id: spotify user id
        :param playlist_name: the friendly name of the playlist we're checking for
        """
        playlist_id = self.get_playlist_id_from_name(user_id, playlist_name)

        playlists = []

        try:
            playlists = self.auth_spotipy.user_playlists(user_id)
        except:
            e = sys.exc_info()[0]
            logging.error('error in getting playlist {playlist_id} for user {user}: {e}'.format(
                user=user_id, playlist_id=playlist_id, e=e))
            raise

        for playlist in playlists['items']:
            if playlist['owner']['id'] == user_id and playlist['id'] == playlist_id:
                return True

        return False

    def get_track_ids_from_track_info(self, track_info):
        """
        Returns the best guess track id for the supplied track info

        :param track_info: A list of dictionaries containing either 'artist' and 'track' keys or a 'blob'
        """
        track_ids = []

        for track in track_info:
            track_id = self.get_track_id_from_track_info(track)

            logging.info("retrieved track id {} for {}".format(track_id, track))

            track_ids.append(track_id)

        return track_ids

    def get_track_id_from_track_info(self, track_info):

        returned_tracks = None

        try:
            returned_tracks = self.search_track(track_info)['tracks']['items']
        except:
            e = sys.exc_info()[0]
            logging.error('error in searching for track {track}: {e}'.format(track=track_info, e=e))
            raise

        if len(returned_tracks) == 0:
            logging.warning('Unable to retrieve id for {track}, skipping'.format(track=track_info))
            return 0

        return returned_tracks[0]['id']

    def search_track(self, track_info, limit=1):
        """
        Gets list of possible tracks for the supplied track information

        :param track_info: A list of dictionaries containing either 'artist' and 'track' keys or a 'blob'
        """
        logging.debug('track info {track_info}'.format(track_info=track_info))

        query = None

        try:
            query = '{track} {artist}'.format(track=track_info['track'], artist=track_info['artist'])
        except:
            query = '{}'.format(track_info['blob'])

        logging.info('searching spotify with query {query}'.format(query=query))

        try:
            retrieved_tracks = self.ccm_spotipy.search(query, limit=limit)
        except:
            e = sys.exc_info()[0]
            logging.error('error in retrieving tracks for {track_info}... error: {error}'.format(
                track_info=track_info, error=e))
            raise

        logging.debug('retrieved tracks {tracks}'.format(tracks=retrieved_tracks))

        return retrieved_tracks