class Movie:
    def __init__(self, code, name, rate, votes, year, genres, imdb_id):
        self.code = code
        self.name = name
        self.rate = rate
        self.votes = votes
        self.dates = []
        self.year = year
        self.genres = genres
        self.imdb_id = imdb_id
        self.imdb_url = f"https://www.imdb.com/title/tt{self.imdb_id}"

    def add_date(self, date):
        self.dates.append(date)

    def set_rate(self, rate):
        self.rate = rate

    def set_voters(self, votes):
        self.votes = votes

    def __repr__(self):
        return f"{self.name} ({self.year}): {self.rate}/10 ({self.votes})"

    def __eq__(self, other):
        return self.rate == other.rate and self.votes == other.votes

    def __lt__(self, other):
        return self.rate < other.rate

    def __iter__(self):
        yield str(self.name)
        yield str(self.year)
        yield str(self.rate)
        yield str(self.votes)
        yield str(self.imdb_url)
