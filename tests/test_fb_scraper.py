import unittest
import logging
from datetime import datetime

from common import posts
from common.posts import facebook_post
from common.posts.facebook_post import FacebookPost as FacebookPost

from common import scrapers
from common.scrapers import facebook_scraper
from common.scrapers.facebook_scraper import FacebookScraper as FacebookScraper

import os, sys
sys.path.insert(0, os.path.abspath('..'))

#YYYY-MM-DD
date_fmt = "%Y-%m-%d"

class TestFacebookScraper(unittest.TestCase):

	def setUp(self):
		logging.info(self.id())

	def tearDown(self):
		pass

	#TODO create a test group to verify this funcitonality

	#Ambient techno world 1990s
	def test_basic_scrape(self):

		begin = "2017-10-07"
		end = "2017-10-08"
		dates_oct_8 = (begin, end)

		fb_criteria = {
			'app_id' : os.environ['FB_APP_ID'],
			'app_secret' : os.environ['FB_APP_SECRET'],
			'group_id': '155783244468120',
			'date_range' : dates_oct_8
			#'authors' = ["David Moufang"]
		}

		#Don't specify author for basic test
		scraper = FacebookScraper(fb_criteria)
		scraper.scrape()
		posts = scraper.get_scraped_posts()

		#Print posts to console
		for post in posts:
			print(post)
