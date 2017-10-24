#Scrape a facebook group and add to a specified user's playlist
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import argparse
import spotipy
import re

from common import posts
from common.posts import facebook_post
from common.posts.facebook_post import FacebookPost as FacebookPost

from common import scrapers
from common.scrapers import facebook_scraper
from common.scrapers.facebook_scraper import FacebookScraper as FacebookScraper

from common import players
from common.players import spotify
from spotify import SpotifyPlayer



def scrape_fb_group_to_spotify_playlist(**kwargs):
	#Create critera object for scraping, refactor this
	fb_criteria = FacebookCriteria(date_range,authors,min_likes,min_loves,limit);
	fb_criteria.app_id=fb_app_id
	fb_criteria.app_secret=fb_app_secret
	fb_criteria.group_id=fb_group_id

	fb_scraper = FacebookScraper(fb_criteria)
	fb_scraper.scrape()
	fb_group_friendly_name = fb_scrper.get_group_friendly_name()

	scraped_track_ids = []

	#Parse all scraped posts, then get their track ids, then add these?
	#Parse one post, get it's track id, and then add in bulk
	spotify_player = SpotifyPlayer()

	for post in fb_scraper.scrape_data:
		track_info = parse_track_and_artist(post)
		track_id = spotify_player.get_track_id_from_track_info(track_info)
		scraped_track_ids.append(track_id)

	playlist_id = spotify_player.create_playlist(fb_group_friendly_name)

	spotify_player.add_tracks_to_playlist(scraped_track_ids, playlist_id)


def get_criteria_from_user(**kwargs):
	pass

def parse_track_and_artist(fb_post):
	"""
	Attempt to parse a particular FB post for a track name and artist

	:param fb_post: post object scraped from a particular fb page
	"""
	#Common track formats
	#ARTIST - TRACK (YEAR)
	#ARTIST - TRACK (Remix)(Official Video)
	#ARTIST - TRACK (Remix)(Official Video)
	#ARTIST - TRACK [Label information]
	#Keep track name with remix information, remove official video or label info
	track_info = None
	link_name = fb_post.link_name

	#remove (Official Video) from title
	re.sub(r'\([(O|o)fficial (v|V)ideo]*\)', '', link_name)

	#remove label information
	re.sub(r'\[[^\]]*\]', '', link_name)

	#remove year from title
	re.sub(r'\(\d{4}\)', '', link_name)

	link_name_split = link_name.split('-')

	if len(link_name_split) == 1:
		track_info = {'blob': link_name}
	else:
		track_info = {'artist': link_name_split[0], 'track': link_name_split[1]}

	return track_info

def validate_arguments(**kwargs):
	#check first for environment variables for id and secret
	if 'fb_app_id' not in kwargs:
		try:
			kwargs['fb_app_id'] = os.environ['FB_APP_ID']
		except:
			print('fb app id not passed nor set in environment')
			exit(1)

	if 'fb_app_secret' not in kwargs:
		try:
			kwargs['fb_app_secret'] = os.environ['FB_APP_SECRET']
		except:
			print('fb app secret not passed in or set in environment')
			exit(1)

	if 'spfy_app_id' not in kwargs:
		try:
			kwargs['spfy_app_id'] = os.environ['SPOTIPY_CLIENT_ID']
		except:
			print('spotify app id not passed nor set in environment')
			exit(1)

	if 'spfy_app_secret' not in kwargs:
		try:
			kwargs['spfy_app_secret'] = os.environ['SPOTIPY_CLIENT_SECRET']
		except:
			print('spotify app secret not passed in nor set in environment')
			exit(1)

	if 'fb_group_id' not in kwargs:
		print('group id not specified')
		exit(1)

	if 'spfy_user_id' not in kwargs:
		print('spotify user id not specified, tracks will not be added to playlist')

	#Read from user if not silent and unspecified
	if not silent and len(authors)==0 and len(date_range)==0 and min_likes==0 and min_loves==0 and limit==0:
		get_criteria_from_user(kwargs)

def parse_arguments():
	parser = argparse.ArgumentParser(description='scrape facebook posts into a spotify playlist')
	parser.add_argument('fb_group_id', metavar='group_id', type=int, help='group id number for the facebook group to scrape')
	parser.add_argument('spotify_id', metavar='username', type=str, help='username for spotify account')
	parser.add_argument('--fb_app_id', type=str, help='facebook app id registered for use with graph api. This overrides any value stored in the FB_APP_ID environment variable')
	parser.add_argument('--fb_app_secret', type=str, help='facebook app secret. This overrides any value stored in the FB_APP_SECRET environment variable')
	parser.add_argument('--spotify_app_id', type=str, help='spotify app id. This overrides any value stored in the SPOTIPY_CLIENT_ID environment variable')
	parser.add_argument('--spotify_app_secret', type=str, help='spotify app secret. This overrides any value stored in the SPOTIPY_CLIENT_SECRET environment variable')
	#TODO: specify format
	parser.add_argument('--begin_date', type=str, help='begin date range for scraping the supplied facebook group')
	parser.add_argument('--end_date', type=str, help='end date range for scraping the supplied facebook group')
	parser.add_argument('--authors', type=str, nargs='+', help='specify list of authors whose posts we want')
	parser.add_argument('--min_likes', type=int, help='minimum number of likes required to scrape a post into our playlist')
	parser.add_argument('--min_loves', type=int, help='minimum number of loves required to scrape a post into our playlist')
	parser.add_argument('--limit', type=int, help='limit the maximum number of tracks to add to our scraped playlist')
	parser.parse_args()


if(__name__=="__main__"):
	arguments = vars(parse_arguments())
	validate_arguments(arguments)
	scrape_fb_group_to_spotify_playlist(arguments)