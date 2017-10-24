#definition for api to create spotify playlist and check if track exists in service

import sys, os
sys.path.insert(0, os.path.abspath('..'))

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

	def create_playlist(self, playlist_name, description):
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

	def add_track_ids_to_playlist(self, track_ids, playlist_id):
		try:
			auth_spotipy.use_playlist_add_tracks(self.user_id, playlist_id, track_ids)
		except:
			e = sys.exc_info()[0]
			logging.error('error in adding tracks {tracks} to playlist {playlist} for user {user}'.format(
				tracks=track_ids, playlist=playlist_id, user=self.user_id))
			raise

	def add_track_to_playlist_by_name(self, track_info, playlist_id):
		"""
		Adds a track to the specified playlist id using track_info as a best-guess

		:param track_info: A dictionary containing either 'artist' and 'track' keys or a 'blob'
		:param playlist_id: spotify's numerical representation of a particular playlist
		"""
		track_id = get_track_id_from_track_info(track_info)
		add_track_to_playlist_by_id(track_id, playlist_id)

	def add_track_to_playlist_by_id(self, track_id, playlist_id):
		pass


	def get_playlist_id_from_name(self, playlist_name, user_name=''):
		"""
		:param playlist_name: friendly name of the playlist
		:param username: username whose playlist we want
		"""
		if user_name == '':
			user_name = self.user_id

		try:
			playlists = self.spotify.auth_spotipy.user_playlists(username)
		except:
			e = sys.exc_info()[0]
			logging.error('error in getting playlist for user {user}: {playlist_name}'.format(user=user_name, playlist_name=playlist_name))
			raise

        for playlist in playlists['items']:
            if playlist['owner']['id'] == username and playlist['name'] == playlist_name:
                return playlist['id']

        raise Exception('no playlist with name {name} found in {user}\'s account'.format(name=playlist_name,user=user_name))

    def get_track_id_from_track_info(self, track_info):
    	"""
    	Returns the best guess track id for the supplied track info

    	:param track_info: A dictionary containing either 'artist' and 'track' keys or a 'blob'
    	"""
    	return search_track(track_info)['tracks']['items'][0]['id']

	def search_track(self, track_info, limit=1):
		"""
		Gets list of possible tracks for the supplied track information

		:param track_info: A dictionary containing either 'artist' and 'track' keys or a 'blob'
		"""
		logging.debug('track info {track_info}'.format(track_info=track_info))

		query = None

		try:
			query = '{track} {artist}'.format(track=track_info['track'], artist=track_info['artist'])
		except:
			query = track_info['blob']

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