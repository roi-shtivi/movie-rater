#!/usr/bin/env python
"""List Planet movies with IMDb rating.
Usage:
    planet.py [options]

Options:
    -h --help                     Show this message and exit.
    -V --version                  Show version information and exit.
    -v --verbose                  Show unnecessary extra information.
    -c CINEMA --cinema=CINEMA     Cinema title (Ayalon/Haifa/Rishon LeZion/Jerusalem/Be'er Sheva/Zikhron Ya'akov)
                                  [default: Rishon LeZion]
    -ht PATH --html=PATH          Export .html file with the table
    -lf PATH --log-file=PATH      Path of log file  [default: planet.log]
"""

import os.path
from docopt import docopt
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import re
import logging
import pandas as pd
from imdb import Cinemagoer
from imdb._exceptions import IMDbParserError
import Levenshtein
from datetime import (datetime, timedelta)
from movie import Movie


# Ignore the insecure warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

CINEMA_CODES = {"Ayalon": 1025,
                "Haifa": 1070,
                "Rishon LeZion": 1072,
                "Jerusalem": 1073,
                "Be'er Sheva": 1074,
                "Zikhron Ya'akov": 1075
                }
# Expensive type of movies.
MACBOOK = {'3d', '4dx', 'hfr-3d', 'imax', 'screenx', 'vip'}

PREFIX_URL = "https://www.planetcinema.co.il/il/data-api-service/v1"

URLS = {
    'posters': f"{PREFIX_URL}/poster/10100/by-showing-type/SHOWING?lang=he_IL&ordering=desc",
    'events': f"{PREFIX_URL}/quickbook/10100/film-events/in-cinema/{{}}/at-date/{{}}?attr=&lang=he_IL",
    'dates': f"{PREFIX_URL}/quickbook/10100/dates/in-cinema/{{}}/until/{{}}?attr=&lang=he_IL",
    'attributes': f"{PREFIX_URL}/quickbook/10100/attributes?jsonp&lang=he_IL"
    }

ia = Cinemagoer()


def get_logger(level=logging.INFO, log_file='planet.log'):
    logger = logging.getLogger(__name__, )
    logger.setLevel(level)
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def json_response(url):
    """
    Send a GET request to the `url`
    :param url: The URL we wish to communicate with
    :return: A JSON format response
    """
    headers = {'User-Agent': 'Mozilla/5.0'}

    session = requests.Session()

    # Get the page
    res = session.get(url, headers=headers)
    # Load into json
    try:
        return json.loads(res.text)
    except json.decoder.JSONDecodeError:
        logger.error(res)


def get_dates_url(cinema_code):
    """
    Generate URL that request the available dates of filming in the desired cinema
    :param cinema_code: numeric code of the desired cinema
    :return: The crafted URL
    """
    now = datetime.now() + timedelta(days=365)
    formatted_date = now.strftime("%Y-%m-%d")
    return URLS['dates'].format(str(cinema_code), formatted_date)


def get_dates(cinema_code):
    """
    Get all the known dates which the cinema is screening films.
    :param cinema_code: numeric code of the desired cinema
    :return: list of dates in %Y-%m-%d format.
    """
    dates = []
    dates_url = get_dates_url(cinema_code)
    dates_json = json_response(dates_url)
    for date in dates_json['body']['dates']:
        dates.append(date)
    return dates


def map_poster_to_matching_movie(movie_name, release_year):
    """
    @param movie_name: The title name of the movie as it found in Planet database
    @param release_year: The year the movie was first released to cinemas as it found in Planet database
    retrieve movie rating data from the Internet Movie Database (IMDB)
    @return: rating of the movie (0<=rating<=10) and the number of votes.
    """
    def _best_matching_movie(movie):
        """
        Define the numerical relevance score for the different IMDB movies that came in the search result
        when searching for `movie_name`.
        :param movie: A IMDb movie object
        :return: A tuple representing the relevance score.
        """
        return (Levenshtein.distance(movie_name, movie.get('title').lower()),
                (0 - movie.get('votes', 0)),
                )
    current_year = datetime.now().year
    # Filter movies only (no episodes)

    optional_movies = ia.search_movie(movie_name)
    # Filter movies only (no episodes) with release years between IMDb and Planet which don't differ for more than 5
    # without upcoming
    s_result = [x for x in optional_movies if
                x.get('kind') == 'movie' and
                x.get('year') is not None and
                (abs(int(x.get('year')) - int(release_year)) <= 5) and
                not (x.get('year') > current_year)]
    if not s_result:
        return None

    # Update votes
    for movie in s_result:
        ia.update(movie, ['main', 'vote details'])

    # Movie with the latest release date
    best_match = min(s_result, key=_best_matching_movie)

    if best_match.get('rating') is None or best_match.get('votes') is None:
        return None
    return best_match


def get_movies(cinema_name):
    """
    Collect all the available movies with their rating and dates
    :param cinema_name: title of the desired cinema
    :return: dictionary of movies where the key is the movie id and value is the Movie object.
    """
    cinema_code = CINEMA_CODES[cinema_name]
    movies = {}
    uncaught = []
    genres = set(json_response(URLS['attributes'])['body']['dropdownConfig']['genres'])
    poster_json = json_response(URLS['posters'])
    # Get the movies names
    for poster in poster_json['body']['posters']:
        # Extract movie title from poster's url
        try:
            movie_name = re.sub('-', ' ', re.search(r'films/([a-z0-9\-]+)', poster['url']).group(1))
            movie_name = re.sub('(.*)(\s*(green|purple))', '\g<1>', movie_name).strip()
            if movie_name in {movie.title for movie in movies.values()}:
                continue
        except (AttributeError, IndexError):
            logger.warning("Could not find movie title of this url: {}".format(poster['url']))
            continue
        try:
            release_year = datetime.strptime(poster['dateStarted'].split('T')[0], "%Y-%m-%d").year
            movie_genres = genres.intersection(set(poster['attributes']))

            # If no Poster genres found in Planet, it's probably a 'fake' movie
            if not movie_genres:
                raise RuntimeError
            selected_movie = map_poster_to_matching_movie(movie_name, release_year)
            if selected_movie is None:
                raise RuntimeError
        except (IMDbParserError, RuntimeError):
            uncaught.append(movie_name)
            continue
        movies[poster['code']] = Movie(poster['code'],
                                       selected_movie.get('title'),
                                       poster['featureTitle'],
                                       selected_movie.get('rating'),
                                       selected_movie.get('votes'),
                                       selected_movie.get('year'),
                                       movie_genres,
                                       selected_movie.get('imdbID'),
                                       poster['url']
                                       )
    # Add screening dates
    dates = get_dates(cinema_code)
    for day in dates:
        movies_json = json_response(URLS['events'].format(cinema_code, day))
        for event in movies_json['body']['events']:
            if not MACBOOK.intersection(set(event['attributeIds'])):
                try:
                    movies[event['filmId']].add_date(event['eventDateTime'])
                except KeyError:
                    continue
    logger.warning(f"Couldn't find result(s) for movie(s): {uncaught}")
    return movies, uncaught


if __name__ == '__main__':
    # Grab the arguments
    args = docopt(__doc__, version='0.1')
    verbose = args['--verbose']
    cinema = args['--cinema']
    html = args['--html']
    log_file = args['--log-file']

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR
    logger = get_logger(level=log_level, log_file=log_file)

    movies, uncaught = get_movies(cinema)

    df = pd.DataFrame(data=sorted(movies.values(), reverse=True),
                      columns=["Title",
                               "Year",
                               "Rating",
                               "Votes",
                               "Genre(s)",
                               "Feature Title",
                               "_planet_url",
                               "_imdb_url"],
                      )
    if html:
        def _craft_html_hyperlink(url, title):
            return f'<a href="{url}" target="_blank">{title}</a>'

        df['Title'] = df.apply(lambda x: _craft_html_hyperlink(x['_imdb_url'], x['Title']),
                               axis=1)
        df['Feature Title'] = df.apply(lambda x: _craft_html_hyperlink(x['_planet_url'], x['Feature Title']),
                                       axis=1)
        # Drop irrelevant columns from the DF
        df = df.drop(['_planet_url', '_imdb_url'], axis=1)
        # Generate the HTML table
        df.to_html(html, index=False, classes='table movies-table', escape=False)

        with open(os.path.join(ROOT_DIR, 'index.html'), 'r') as f:
            content = f.read()

        uncaught_message = f'<p id="uncaught">Could not find result(s) for movie(s): {uncaught}</p>'
        content = re.sub(r'<p id="uncaught">.*</p>', f"{uncaught_message}", content, re.M)

        execution_date_message = f'<p id="execution-time">Executed at: {datetime.now()}</p>'
        content = re.sub(r'<p id="execution-time">.*</p>', f"{execution_date_message}", content, re.M)

        with open(os.path.join(ROOT_DIR, 'index.html'), 'w') as f:
            f.write(content)

    print(df.to_markdown())
