import requests
import json
import re
import imdb
import Levenshtein
from datetime import datetime
from datetime import timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from movie import Movie

# Ignore the insecure warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

cinema_codes = {"Ayalon": 1025,
                "Haifa": 1070,
                "Rishon LeZion": 1072,
                "Jerusalem": 1073,
                "Be'er Sheva": 1074,
                "Zikhron Ya'akov": 1075
                }
# expensive type of movies.
macbook = {'3d', '4dx', 'hfr-3d', 'imax', 'screenx', 'vip'}

urls = {
    'posters': "https://www.yesplanet.co.il/il/data-api-service/v1/poster/10100/by-showing-type/SHOWING?lang=he_IL&ordering=desc",
    'events': "https://www.yesplanet.co.il/il/data-api-service/v1/quickbook/10100/film-events/in-cinema/{}/at-date/{}?attr=&lang=he_IL",
    'dates': "https://www.yesplanet.co.il/il/data-api-service/v1/quickbook/10100/dates/in-cinema/{}/until/{}?attr=&lang=he_IL",
    'attributes': "https://www.yesplanet.co.il/il/data-api-service/v1/quickbook/10100/attributes?jsonp&lang=he_IL"
    }

ia = imdb.IMDb()


def json_response(url):
    # Get the page
    res = requests.get(url, verify=False)
    # Load into json
    return json.loads(res.text)


def get_dates_url(cinema_code):
    """
    generate url that request the available dates of filming in the desired cinema
    :param cinema_code: numeric code of the desired cinema
    :return: url
    """
    now = datetime.now() + timedelta(days=365)
    formatted_date = now.strftime("%Y-%m-%d")
    return urls['dates'].format(str(cinema_code), formatted_date)


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


def get_vote_details(movie_name):
    """
    retrieve movie rating data from the Internet Movie Database (IMDB)
    :return: rating of the movie (0<=rating<=10) and the number of votes.
    """
    current_year = datetime.now().year
    # filter movies only (no episodes)
    s_result = [x for x in ia.search_movie(movie_name) if
                x.get('kind') == 'movie' and
                x.get('year') is not None and
                x.get('year') <= current_year]
    if not s_result:
        return None
    # movie with the latest release date
    minimum = min(s_result, key=lambda movie: (abs(movie.data['year'] - current_year), Levenshtein.distance(movie_name, movie.get('title'))))
    if minimum.get('rating') is None:
        ia.update(minimum, ['main', 'vote details'])
    rating = {'rating': minimum.get('rating'), 'votes': minimum.get('votes')}
    if rating['rating'] is None or rating['votes'] is None:
        return None
    return rating


def get_movies(cinema_name):
    """
    Collect all the available movies with their rating and dates
    :param cinema_name: name of the desired cinema
    :return: dictionary of movies where the key is the movie id and value is the Movie object.
    """
    cinema_code = cinema_codes[cinema_name]
    movies = {}
    uncatched = []
    genres = set(json_response(urls['attributes'])['body']['dropdownConfig']['genres'])
    poster_json = json_response(urls['posters'])
    # Get the movies names
    for poster in poster_json['body']['posters']:
        # extract movie name from poster's url
        try:
            movie_name = re.sub('-', ' ', re.search(r'films/([a-z\-]+)', poster['url']).group(1))
        except [AttributeError, IndexError]:
            print("could not find movie name of this url: {}".format(poster['url']))
            continue
        vote_details = get_vote_details(movie_name)
        movie_genres = genres.intersection(set(poster['attributes']))
        if vote_details is None:
            uncatched.append(movie_name)
            continue
        movies[poster['code']] = Movie(poster['code'], movie_name, vote_details['rating'],
                                       vote_details['votes'], movie_genres)
    # add screening dates
    dates = get_dates(cinema_code)
    for day in dates:
        movies_json = json_response(urls['events'].format(cinema_code, day))
        for event in movies_json['body']['events']:
            if not macbook.intersection(set(event['attributeIds'])):
                try:
                    movies[event['filmId']].add_date(event['eventDateTime'])
                except KeyError:
                    continue
    return movies


if __name__ == '__main__':
    movies = get_movies("Rishon LeZion")
    for movie in sorted(movies.values(), reverse=True):
        print(movie)