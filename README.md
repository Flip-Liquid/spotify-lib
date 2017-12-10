# Spotify-scraper

## Usage

1. [Create a Spotify application tied to your spotify account](https://beta.developer.spotify.com/dashboard/). This is to enable searching the spotify library and adding to your playlist

2. [Create a Facebook application tied to your facebook account](https://developers.facebook.com/apps/). This is to enable access to public groups.

3. Install spotipy.

4. Export the following variables to your current bash session (or, alternatively, specify on command line):

```bash
export SPOTIPY_CLIENT_ID='<your spotify application client id>'
export SPOTIPY_CLIENT_SECRET='<your spotify application client secret>'
export FB_APP_ID='<your facebook application client id>'
export FB_APP_SECRET='<your facebook application secret>'
```

## Unit tests

To run tests, use python3 -m unittest discover

## Credits

Max Woolf - [Facebook Page Post Scraper](https://github.com/minimaxir/facebook-page-post-scraper)

Paul Lamere - [Spotipy](https://github.com/plamere/spotipy)

## License

MIT