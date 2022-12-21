#!/usr/bin/env python

import requests
import json
import re
from imdb import Cinemagoer
from imdb._exceptions import IMDbParserError
import Levenshtein
from datetime import datetime
from datetime import timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
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


def json_response(url):
    headers = {'User-Agent': 'Mozilla/5.0'}

    session = requests.Session()

    # Get the page
    res = session.get(url, headers=headers)
    # Load into json
    try:
        return json.loads(res.text)
    except json.decoder.JSONDecodeError:
        print(res)


def get_dates_url(cinema_code):
    """
    generate url that request the available dates of filming in the desired cinema
    :param cinema_code: numeric code of the desired cinema
    :return: url
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


def map_poster_to_matching_movie(movie_name):
    """
    retrieve movie rating data from the Internet Movie Database (IMDB)
    :return: rating of the movie (0<=rating<=10) and the number of votes.
    """
    def _best_matching_movie(movie):
        """
        Define the numerical relevance score for the different IMDB movies that came in the search result
        when searching for `movie_name`.
        :param movie: A IMDB movie object
        :return: A tuple representing the relevance score.
        """
        return (Levenshtein.distance(movie_name, movie.get('title')),
                abs(movie.data['year'] - current_year))
    current_year = datetime.now().year
    # Filter movies only (no episodes)

    # Waiting for fix of https://github.com/cinemagoer/cinemagoer/issues/426
    s_result = [x for x in ia.search_movie(movie_name) if
                x.get('kind') == 'movie' and
                x.get('year') is not None and
                x.get('year') <= current_year]
    if not s_result:
        return None
    # Movie with the latest release date
    best_match = min(s_result, key=_best_matching_movie)
    if best_match.get('rating') is None:
        ia.update(best_match, ['main', 'vote details'])
    if best_match.get('rating') is None or best_match.get('votes') is None:
        return None
    return best_match


def get_movies(cinema_name):
    """
    Collect all the available movies with their rating and dates
    :param cinema_name: name of the desired cinema
    :return: dictionary of movies where the key is the movie id and value is the Movie object.
    """
    cinema_code = CINEMA_CODES[cinema_name]
    movies = {}
    uncaught = []
    genres = set(json_response(URLS['attributes'])['body']['dropdownConfig']['genres'])
    poster_json = json_response(URLS['posters'])
    # Get the movies names
    for poster in poster_json['body']['posters']:
        # Extract movie name from poster's url
        try:
            movie_name = re.sub('-', ' ', re.search(r'films/([a-z0-9\-]+)', poster['url']).group(1))
            movie_name = re.sub('(.*)(\s*(green|purple))', '\g<1>', movie_name).strip()
            if movie_name in {movie.name for movie in movies.values()}:
                continue
        except (AttributeError, IndexError):
            print("could not find movie name of this url: {}".format(poster['url']))
            continue
        try:
            selected_movie = map_poster_to_matching_movie(movie_name)
            movie_genres = genres.intersection(set(poster['attributes']))
            if selected_movie is None:
                raise RuntimeError
        except (IMDbParserError, RuntimeError) as e:
            print(e)
            uncaught.append(movie_name)
            continue
        movies[poster['code']] = Movie(poster['code'],
                                       selected_movie.get('title'),
                                       selected_movie.get('rating'),
                                       selected_movie.get('votes'),
                                       selected_movie.get('year'),
                                       movie_genres
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
    print(f"Could'nt find result(s) for movie(s): {uncaught}")
    return movies


if __name__ == '__main__':
    movies = get_movies("Rishon LeZion")
    print("*** Movie score list: ***")
    for movie in sorted(movies.values(), reverse=True):
        print(movie)
