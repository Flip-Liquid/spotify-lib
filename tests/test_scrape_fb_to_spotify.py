#TODO: make this a formal UT
import os, sys
sys.path.insert(0, os.path.abspath('..'))

import scripts
from scripts import scrape_fb_group_to_spotify

def test_scrape_and_dump():
	test_arguments = {
		"spfy_user_id": "kkdoom",
		"fb_group_id": "251212474910393",
		"begin_date": "2017-10-07",
		"end_date": "2017-11-01",
		"scrape_only": True,
		"min_likes": None,
		"min_loves": None,
		"limit": None,
		"no_dump": False,
		"out_file": None
	}

	scrape_fb_group_to_spotify.validate_arguments(test_arguments)
	scrape_fb_group_to_spotify.scrape_fb_group_to_spotify_playlist(**test_arguments)

test_scrape_and_dump()