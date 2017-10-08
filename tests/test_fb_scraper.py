import unittest
import logging
from datetime import datetime

from common import criteria
from common.criteria import facebook_criteria
from common.criteria.facebook_criteria import FacebookCriteria as FacebookCriteria

from posts import facebook_post
from posts.facebook_post import FacebookPost as FacebookPost

from scrapers import facebook_scraper
from scrapers.facebook_scraper import FacebookScraper as FacebookScraper

#YYYY-MM-DD
date_fmt = "%Y-%m-%d"

class TestScraper(unittest.TestCase):

	def setUp(self):
		logging.info(self.id())

	def tearDown(self):
		pass

	#TODO create a test group to verify this funcitonality
	def test_basic_scrape(self):
		fb_criteria = FacebookCriteria()
		fb_criteria.app_id = "125411544789715"
		fb_criteria.app_secret = "cccd85883b5843b282da3b2d32bb2118" 
		#Ambient techno world 1990s
		fb_criteria.group_id = "155783244468120"

		#check just today
		begin = "2017-10-07"
		end = "2017-10-08"
		dates_oct_8 = (begin, end)

		print(dates_oct_8)

		fb_criteria.date_range = dates_oct_8

		#Don't specify author for basic test
		#fb_criteria.authors = ["David Moufang"]
		scraper = FacebookScraper(fb_criteria)
		scraper.scrape()
		posts = scraper.get_scraped_posts()

		#Print posts to console
		for post in posts:
			print(post)
