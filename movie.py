class Movie:
    def __init__(self, code, name, rate, votes, genres):
        self.code = code
        self.name = name
        self.rate = rate
        self.votes = votes
        self.dates = []
        self.genres = genres

    def add_date(self, date):
        self.dates.append(date)

    def set_rate(self, rate):
        self.rate = rate

    def set_voters(self, votes):
        self.votes = votes

    def __repr__(self):
        return "{}: {}/10 ({})".format(self.name, self.rate, self.votes)

    def __eq__(self, other):
        return self.rate == other.rate and self.votes == other.votes

    def __lt__(self, other):
        return self.rate < other.rate
