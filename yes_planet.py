import requests
import json
import imdb
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

poster_url = "https://www.yesplanet.co.il/il/data-api-service/v1/poster/10100/by-showing-type/SHOWING?lang=he_IL&ordering=desc"
film_event_url = "https://www.yesplanet.co.il/il/data-api-service/v1/quickbook/10100/film-events/in-cinema/{}/at-date/{}?attr=&lang=he_IL"

ia = imdb.IMDb()


def get_dates_url(cinema_code):
    """
    generate url that request the available dates of filming in the desired cinema
    :param cinema_code: numeric code of the desired cinema
    :return: url
    """
    now = datetime.now() + timedelta(days=365)
    formatted_date = now.strftime("%Y-%m-%d")
    return "https://www.yesplanet.co.il/il/data-api-service/v1/quickbook/10100/dates/in-cinema/{}/until/{}?attr=&lang=he_IL". \
        format(str(cinema_code), formatted_date)


def get_dates(cinema_code):
    """
    Get all the known dates which the cinema is screening films.
    :param cinema_code: numeric code of the desired cinema
    :return: list of dates in %Y-%m-%d format.
    """
    dates = []
    dates_url = get_dates_url(cinema_code)
    date_response = requests.get(dates_url, verify=False)
    dates_json = json.loads(date_response.text)
    for date in dates_json['body']['dates']:
        dates.append(date)
    return dates


def get_vote_details(movie_name):
    """
    retrieve movie rating data from the Internet Movie Database (IMDB)
    :return: rating of the movie (0<=rating<=10) and the number of votes.
    """
    # filter movies only (no episodes)
    s_result = [x for x in ia.search_movie(movie_name) if x.get('kind') == 'movie' and x.get('year') is not None]
    # movie with the latest release date
    maxi = max(s_result, key=lambda movie: movie.data['year'])
    if maxi.get('rating') is None:
        ia.update(maxi, ['main', 'vote details'])
    return {'rating': maxi.get('rating'), 'votes': maxi.get('votes')}


def get_movies(cinema_name):
    """
    Collect all the available movies with their rating and dates
    :param cinema_name: name of the desired cinema
    :return: dictionary of movies where the key is the movie id and value is the Movie object.
    """
    cinema_code = cinema_codes[cinema_name]
    movies = {}
    uncatched = []
    response = requests.get(poster_url, verify=False)
    # Load into json
    poster_json = json.loads(response.text)
    # Get the movies names
    for poster in poster_json['body']['posters']:
        movie_name = poster['url'][7:].replace("-", " ")
        vote_details = get_vote_details(movie_name)
        if vote_details['rating'] is None or vote_details['votes'] is None:
            uncatched.append(movie_name)
            continue
        movies[poster['code']] = Movie(poster['code'], movie_name, vote_details['rating'],
                                       vote_details['votes'])  # remove the '/films/' prefix

    dates = get_dates(cinema_code)
    for day in dates:
        # Get the page
        response = requests.get(film_event_url.format(cinema_code, day), verify=False)
        # Load into json
        movies_json = json.loads(response.text)
        for event in movies_json['body']['events']:
            if not macbook.intersection(set(event['attributeIds'])):
                movies[event['filmId']].add_date(event['eventDateTime'])

    return movies


if __name__ == '__main__':
    movies = get_movies("Rishon LeZion")
    print(sorted(movies.values(), reverse=True))
