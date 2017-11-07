#Scrape a facebook group and add to a specified user's playlist
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import argparse
import re
import csv
from datetime import datetime

from common import posts
from common.posts import facebook_post
from common.posts.facebook_post import FacebookPost as FacebookPost

from common import scrapers
from common.scrapers import facebook_scraper
from common.scrapers.facebook_scraper import FacebookScraper as FacebookScraper

from common import players
from common.players import spotify
from common.players.spotify import SpotifyPlayer

#if not silent and len(authors)==0 and len(date_range)==0 and min_likes==0 and min_loves==0 and limit==0:

def scrape_fb_group_to_spotify_playlist(**kwargs):
    #Create critera object for scraping, refactor this
    fb_criteria = {
        "app_id"        : kwargs["fb_app_id"],
        "app_secret"    : kwargs["fb_app_secret"],
        "group_id"      : kwargs["fb_group_id"],
        "date_range"    : (kwargs["begin_date"], kwargs["end_date"]),
        "min_likes"     : kwargs["min_likes"],
        "min_loves"     : kwargs["min_loves"],
        "limit"         : kwargs["limit"]
    }

    print('Logging with criteria:')
    print(fb_criteria)

    fb_scraper = FacebookScraper(fb_criteria)
    fb_scraper.scrape()
    fb_group_friendly_name = fb_scraper.get_group_friendly_name()

    dump_info = []
    scraped_track_ids = []

    playlist_name= fb_group_friendly_name + ' {}'.format(datetime.now().strftime('%Y.%m.%d'))

    #Parse all scraped posts, then get their track ids, then add these?
    #Parse one post, get it's track id, and then add in bulk
    spotify_player = SpotifyPlayer(kwargs["spfy_user_id"])

    if not kwargs['no_dump']:
        if kwargs['out_file'] is None:
            kwargs['out_file'] = playlist_name

    for post in fb_scraper.scrape_data:
        track_info = None

        try:
            track_info = parse_track_and_artist(post.link_name)
        except:
            continue

        track_id = 0

        try:
            track_id = spotify_player.get_track_id_from_track_info(track_info)
        except:
            continue

        if track_id != 0:
            scraped_track_ids.append(track_id)

        if kwargs['out_file'] is not None:
            dump_info.append((post.link_name, track_info['artist'], track_info['track'], track_info['blob'], track_id))


    if not kwargs['no_dump']:
        dump_scraped_posts(dump_info, playlist_name, kwargs['out_file'])

    if kwargs['scrape_only']:
        return

    print('adding {num_tracks} tracks to {playlist}'.format(num_tracks=len(scraped_track_ids), playlist=playlist_name))

    playlist_id = spotify_player.create_playlist(playlist_name)

    spotify_player.add_track_ids_to_playlist(scraped_track_ids, playlist_id)

def dump_scraped_posts(scrape_info, groupname, filename):
    """
    Dumps posts from previous scraping to a csv file

    :param scrape_info: tuple of (link name, artist, track, blob, spotify track is)
    :param groupname: name of the facebook group we're scraping
    :param filename: File to dump our scrapejob
    """
    dirname = "scrapes"

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(os.path.join(dirname, filename), 'w') as file:
        w = csv.writer(file)
        w.writerow([groupname])
        w.writerow(["link name", "artist", "track", "blob", "spotify track id"])

        for scraped_post in scrape_info:
            w.writerow(scraped_post)


def get_criteria_from_user(**kwargs):
    pass

def parse_track_and_artist(name):
    """
    Attempt to parse a particular FB post for a track name and artist

    :param name: link name from a post
    """
    #Common track formats
    #ARTIST - TRACK (YEAR)
    #ARTIST - TRACK (Remix)(Official Video) HQ
    #ARTIST - TRACK [Label information]
    #ARTIST "TRACK"
    #ARTIST : TRACK
    #Keep track name with remix information, remove official video or label info
    track_info = None

    #remove any parens
    #name = re.sub(r'\([^()]*?((v|V)ideo)\)', '', name)
    name = re.sub(r'\([^\())]*\)', '', name)

    #remove label information
    name = re.sub(r'\[[^\]]*\]', '', name)

    #remove year from title
    name = re.sub(r'199\d', '', name)

    #Remove "High Quality" from title
    name = re.sub(r'HQ', '', name)

    name_split = name.split('-')

    if len(name_split) == 1:

        print('Unable to parse post as ARTIST - TRACK')
        print(name)

        if(len(name)==0):
            raise Exception('Unable to parse post {}'.format(name))

        track_info = {'blob': name, 'artist': None, 'track': None}
    else:
        track_info = {'artist': name_split[0], 'track': name_split[1], 'blob': None}

    return track_info

def validate_arguments(kwargs):
    #check first for environment variables for id and secret
    if kwargs['fb_app_id'] is None:
        try:
            print('trying to get fb app id from environment')
            kwargs['fb_app_id'] = os.environ['FB_APP_ID']
        except:
            print('fb app id not passed nor set in environment')
            exit(1)

    if kwargs['fb_app_secret'] is None:
        try:
            print('trying to get fb app secret from environment')
            kwargs['fb_app_secret'] = os.environ['FB_APP_SECRET']
        except:
            print('fb app secret not passed in or set in environment')
            exit(1)

    if kwargs['spfy_app_id'] is None:
        try:
            print('trying to get spotify app id from environment')
            kwargs['spfy_app_id'] = os.environ['SPOTIPY_CLIENT_ID']
        except:
            print('spotify app id not passed nor set in environment')
            exit(1)

    if kwargs['spfy_app_secret'] is None:
        try:
            print('trying to get spotify app secret from environment')
            kwargs['spfy_app_secret'] = os.environ['SPOTIPY_CLIENT_SECRET']
        except:
            print('spotify app secret not passed in nor set in environment')
            exit(1)

    if kwargs['fb_group_id'] is None:
        print('group id not specified')
        exit(1)

    if kwargs['spfy_user_id'] is None:
        print('spotify user id not specified, tracks will not be added to playlist')

    #Read from user if not silent and unspecified
    if not kwargs['silent'] and len(kwargs['authors'])==0 and 'begin_date' not in kwargs and 'end_date' not in kwargs and kwargs['min_likes']==0 and kwargs['min_loves']==0 and kwargs['limit']==0:
        get_criteria_from_user(kwargs)



def parse_arguments():
    parser = argparse.ArgumentParser(description='scrape facebook posts into a spotify playlist')
    parser.add_argument('fb_group_id', metavar='group_id', type=int, help='group id number for the facebook group to scrape')
    parser.add_argument('--spfy_user_id', metavar='username', type=str, help='username for spotify account')
    parser.add_argument('--fb_app_id', type=str, help='facebook app id registered for use with graph api. This overrides any value stored in the FB_APP_ID environment variable')
    parser.add_argument('--fb_app_secret', type=str, help='facebook app secret. This overrides any value stored in the FB_APP_SECRET environment variable')
    parser.add_argument('--spfy_app_id', type=str, help='spotify app id. This overrides any value stored in the SPOTIPY_CLIENT_ID environment variable')
    parser.add_argument('--spfy_app_secret', type=str, help='spotify app secret. This overrides any value stored in the SPOTIPY_CLIENT_SECRET environment variable')
    #TODO: specify format
    parser.add_argument('--begin_date', type=str, help='begin date range for scraping the supplied facebook group in format yyyy-mm-dd',default='')
    parser.add_argument('--end_date', type=str, help='end date range for scraping the supplied facebook group yyyy-mm-dd', default='')
    parser.add_argument('--authors', type=str, nargs='+', help='specify list of authors whose posts we want', default=[])
    parser.add_argument('--min_likes', type=int, help='minimum number of likes required to scrape a post into our playlist', default=0)
    parser.add_argument('--min_loves', type=int, help='minimum number of loves required to scrape a post into our playlist', default=0)
    parser.add_argument('--limit', type=int, help='limit the maximum number of tracks to add to our scraped playlist', default=0)
    parser.add_argument('--silent', help='run script without prompting for criteria if none is provided', action='store_const', const=True, default=False)
    parser.add_argument('--scrape_only', help='choose only to scrape data without adding to spotify playlist', action='store_const', const=True, default=False)
    parser.add_argument('--out_file', type=str, help='specify out file for dumping scrape information')
    parser.add_argument('--no_dump', help='set this flag if no output csv is desired', action='store_const', const=True, default=False)
    return parser.parse_args()


if(__name__=="__main__"):
    arguments = vars(parse_arguments())
    print('parsed arguments')
    print(arguments)
    validate_arguments(arguments)
    scrape_fb_group_to_spotify_playlist(**arguments)