#Scrape a facebook group and add to a specified user's playlist
import sys, os
sys.path.insert(0, os.path.abspath('..'))

from common import criteria
from common.criteria import facebook_criteria
from common.criteria.facebook_criteria import FacebookCriteria as FacebookCriteria

from common import posts
from common.posts import facebook_post
from common.posts.facebook_post import FacebookPost as FacebookPost

from common import scrapers
from common.scrapers import facebook_scraper
from common.scrapers.facebook_scraper import FacebookScraper as FacebookScraper

def get_criteria_from_user():
	pass

def scrape_fb_group_to_spotify(fb_group_id='',fb_app_id='',fb_app_secret='',spfy_app_id='',spfy_app_secret='',spfy_user_id='',silent=false,authors=[],date_range=(),min_likes=0,min_loves=0,limit=0):
	#check first for environment variables for id and secret
	if fb_app_id=='' or fb_app_secret=='':
		try:
			fb_app_id = os.environ['FB_APP_ID']
			fb_app_secret = os.environ['FB_APP_SECRET']
		except:
			print('fb app id or fb app secret not passed nor set in environment')
			return

	if spfy_app_id=='' or spfy_app_secret=='':
		try:
			spfy_app_id = os.environ['SPOTIPY_CLIENT_ID']
			spfy_app_secret = os.environ['SPOTIPY_CLIENT_SECRET']
		except:
			print('spotify app id or spotify app secret not passed nor set in environment')
			return

	if fb_group_id='':
		print('group id not specified')
		return

	if spfy_user_id=='':
		print('spotify user id not specified, tracks will not be added to playlist')

	#Read from user if not silent and unspecified
	if !silent and authors=[] and date_range=() and min_likes=0 and min_loves=0 and limit=0:
		(authors,date_range,min_likes,min_loves,limit) = *get_criteria_from_user()

	#Create critera object for scraping, refactor this
	fb_criteria = FacebookCriteria(date_range,authors,min_likes,min_loves,limit);
	fb_criteria.app_id=fb_app_id
	fb_criteria.app_secret=fb_app_secret
	fb_criteria.group_id=fb_group_id

	#init scraper
	fb_scraper = FacebookScraper(fb_criteria)

if(__name__=="__main__"):
	scrape_fb_group_to_spotify(*sys.argv[1:])