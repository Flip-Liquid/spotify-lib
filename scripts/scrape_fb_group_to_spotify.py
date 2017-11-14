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

    track_ids = []
    no_dump = kwargs['no_dump']
    out_file = kwargs['out_file']
    fb_criteria = unpack_fb_critieria_from_args(**kwargs)

    fb_scraper = FacebookScraper(fb_criteria)
    spotify_player = SpotifyPlayer(kwargs['spfy_user_id'])


    if 'in_file' not in kwargs or kwargs['in_file'] is None:
        track_ids = scrape_track_ids_and_dump(fb_criteria, fb_scraper, spotify_player, no_dump, out_file)
    else:
        track_ids = get_track_ids_from_file(kwargs['in_file'])

    playlist_name = generate_playlist_name(fb_scraper)

    print('adding {num_tracks} tracks to {playlist}'.format(num_tracks=len(track_ids), playlist=playlist_name))

    playlist_id = spotify_player.create_playlist(playlist_name)

    spotify_player.add_track_ids_to_playlist(track_ids, playlist_id)

def unpack_fb_critieria_from_args(**kwargs):
    fb_criteria = {
            "app_id"        : kwargs["fb_app_id"],
            "app_secret"    : kwargs["fb_app_secret"],
            "group_id"      : kwargs["fb_group_id"],
            "date_range"    : (kwargs["begin_date"], kwargs["end_date"]),
            "min_likes"     : kwargs["min_likes"],
            "min_loves"     : kwargs["min_loves"],
            "limit"         : kwargs["limit"]
        }
    return fb_criteria

def scrape_track_ids_and_dump(fb_criteria, scraper, spfy, no_dump, out_file):
    #Create critera object for scraping, refactor this
    track_ids = []

    print('Logging with criteria:')
    print(fb_criteria)

    try:
        scraper.scrape()
    except:
        print('Scrape terminated early with error:')
        print(sys.exc_info[0])

    dump_info = None

    playlist_name = generate_playlist_name()

    if not no_dump:
        dump_info = []
        if out_file is None:
            out_file = playlist_name.translate({ord(c): None for c in '!@#$\\/'})

    get_spotify_track_ids(spfy, scraper.scrape_data, track_ids, dump_info)

    if dump_info is not None:
        dump_scraped_posts(dump_info, scraper.get_group_friendly_name(), out_file)

    return track_ids

def generate_playlist_name(scraper):

    fb_group_friendly_name = scraper.get_group_friendly_name()
    playlist_name = fb_group_friendly_name + ' {}'.format(datetime.now().strftime('%Y.%m.%d'))

    return playlist_name

def get_spotify_track_ids(spfy, scraped_data, track_ids, dump_info):
    for post in scraped_data:
        track_info = None
        track_id = 0

        try:
            track_info = parse_track_and_artist(post.link_name)
        except:
            continue
        try:
            track_id = spfy.get_track_id_from_track_info(track_info)
        except:
            continue

        if track_id != 0:
            track_ids.append(track_id)

        if dump_info is not None:
            dump_info.append((post.link_name, track_info['artist'], track_info['track'], track_info['blob'], track_id))

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
    #ARTIST :: TRACK
    #TRACK by ARTIST
    #TODO: Keep track name with remix information, remove official video or label info
    track_info = None

    #remove any parens
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

def get_track_ids_from_file(in_file):
    #link name, artist, track, blob, track_id
    if not os.path.exists(in_file):
        raise Exception('{} does not exist'.format(in_file))

    track_ids = []

    with open(in_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            track_id = row[3]
            if track_id != 0:
                track_ids.append(track_id)

    return track_ids

def validate_arguments(kwargs):
    #check first for environment variables for id and secret
    if 'fb_app_id' not in kwargs or kwargs['fb_app_id'] is None:
        try:
            print('trying to get fb app id from environment')
            kwargs['fb_app_id'] = os.environ['FB_APP_ID']
        except:
            print('fb app id not passed nor set in environment')
            exit(1)

    if 'fb_app_secret' not in kwargs or kwargs['fb_app_secret'] is None:
        try:
            print('trying to get fb app secret from environment')
            kwargs['fb_app_secret'] = os.environ['FB_APP_SECRET']
        except:
            print('fb app secret not passed in or set in environment')
            exit(1)

    if 'spfy_app_id' not in kwargs or kwargs['spfy_app_id'] is None:
        try:
            print('trying to get spotify app id from environment')
            kwargs['spfy_app_id'] = os.environ['SPOTIPY_CLIENT_ID']
        except:
            print('spotify app id not passed nor set in environment')
            exit(1)

    if 'spfy_app_secret' not in kwargs or kwargs['spfy_app_secret'] is None:
        try:
            print('trying to get spotify app secret from environment')
            kwargs['spfy_app_secret'] = os.environ['SPOTIPY_CLIENT_SECRET']
        except:
            print('spotify app secret not passed in nor set in environment')
            exit(1)

    if 'fb_group_id' not in kwargs or kwargs['fb_group_id'] is None:
        print('group id not specified')
        exit(1)

    if 'spfy_user_id' not in kwargs or kwargs['spfy_user_id'] is None:
        print('spotify user id not specified, tracks will not be added to playlist')

    #Read from user if not silent and unspecified
    #if ('silent' not in kwargs or not kwargs['silent']) and len(kwargs['authors'])==0 and 'begin_date' not in kwargs and 'end_date' not in kwargs and kwargs['min_likes']==0 and kwargs['min_loves']==0 and kwargs['limit']==0:
        #get_criteria_from_user(kwargs)



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
    parser.add_argument('--in_file', type=str, help='specify path of a previous dump from which to create the playlist')
    parser.add_argument('--out_file', type=str, help='specify out file for dumping scrape information')
    parser.add_argument('--no_dump', help='set this flag if no output csv is desired', action='store_const', const=True, default=False)
    return parser.parse_args()


if(__name__=="__main__"):
    arguments = vars(parse_arguments())
    print('parsed arguments')
    print(arguments)
    validate_arguments(arguments)
    scrape_fb_group_to_spotify_playlist(**arguments)