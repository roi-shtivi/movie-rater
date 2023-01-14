class Movie:
    def __init__(self, code, title, feature_title, rate, votes, year, genres, imdb_id, planet_url):
        self.code = code
        self.title = title
        self.feature_title = feature_title
        self.rating = rate
        self.votes = votes
        self.year = year
        self.genres = genres
        self.imdb_id = imdb_id
        self.imdb_url = f"https://www.imdb.com/title/tt{self.imdb_id}"
        self.planet_url = planet_url
        self.dates = []

    def add_date(self, date):
        self.dates.append(date)

    def set_rate(self, rate):
        self.rating = rate

    def set_voters(self, votes):
        self.votes = votes

    def __repr__(self):
        return f"{self.title} ({self.year}): {self.rating}/10 ({self.votes})"

    def __eq__(self, other):
        return self.rating == other.rating and self.votes == other.votes

    def __lt__(self, other):
        return self.rating < other.rating

    def __iter__(self):
        yield str(self.title)
        yield str(self.year)
        yield str(self.rating)
        yield str(self.votes)
        yield ', '.join(map(str, self.genres))
        yield str(self.feature_title)
        yield str(self.planet_url)
        yield str(self.imdb_url)
