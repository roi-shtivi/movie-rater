# movie-rater
###Help you find your movie for the weekend using IMDB rating.
###https://shtivi.xyz/movie-rater


### Usage
```commandline
"""List Planet movies with IMDb rating.
Usage:
    planet.py [options]

Options:
    -h --help                     Show this message and exit.
    -V --version                  Show version information and exit.
    -v --verbose                  Show unnecessary extra information.
    -c CINEMA --cinema=CINEMA     Cinema name (Ayalon/Haifa/Rishon LeZion/Jerusalem/Be'er Sheva/Zikhron Ya'akov)
                                  [default: Rishon LeZion]
    -ht PATH --html=PATH          Export .html file with the table
    -lf PATH --log-file=PATH      Path of log file  [default: planet.log]
"""
```

### Installation

```commandline
    pip install -r requirements.txt
```

### Example
```commandline
python planet.py

|    | Title                                        |   Year |   Rating |   Votes |   IMDbID |
|---:|:---------------------------------------------|-------:|---------:|--------:|---------:|
|  0 | Avatar: The Way of Water                     |   2022 |      8   |   87897 |  1630029 |
|  1 | Karaoke                                      |   2022 |      7.9 |     835 | 14300518 |
|  2 | The Fabelmans                                |   2022 |      7.8 |   13850 | 14208870 |
|  3 | Puss in Boots: The Last Wish                 |   2022 |      7.7 |    2088 |  3915174 |
|  4 | Greener Pastures                             |   2022 |      7.7 |      31 | 12961740 |
|  5 | Matchmaking                                  |   2022 |      7.7 |      40 | 22457212 |
|  6 | Triangle of Sadness                          |   2022 |      7.6 |   40110 |  7322224 |
|  7 | Virginity                                    |   2022 |      7.5 |      38 | 21628716 |
|  8 | The Menu                                     |   2022 |      7.5 |   42920 |  9764362 |
|  9 | After Love                                   |   2020 |      7.3 |    3185 | 10692788 |
| 10 | She Said                                     |   2022 |      7.2 |   11084 | 14807308 |
| 11 | DC League of Super-Pets                      |   2022 |      7.2 |   62774 |  8912936 |
| 12 | Mrs. Harris Goes to Paris                    |   2022 |      7.1 |   10705 |  5151570 |
| 13 | Violent Night                                |   2022 |      7   |   20595 | 12003946 |
| 14 | Money Plane                                  |   2021 |      6.9 |      22 | 14667692 |
| 15 | One Piece Film: Red                          |   2022 |      6.9 |    8064 | 16183464 |
| 16 | The Lost King                                |   2022 |      6.6 |    2091 | 13421498 |
| 17 | Smile                                        |   2022 |      6.6 |   79849 | 15474916 |
| 18 | Minions: The Rise of Gru                     |   2022 |      6.6 |   63473 |  5113044 |
| 19 | Rumba Therapy                                |   2022 |      6.5 |     181 | 12071756 |
| 20 | Black Adam                                   |   2022 |      6.5 |  177098 |  6443346 |
| 21 | I Wanna Sleep with You                       |   2015 |      6.4 |       7 |  4076134 |
| 22 | Fall                                         |   2022 |      6.4 |   46545 | 15325794 |
| 23 | Chickenhare and the Hamster of Darkness      |   2022 |      6.3 |    1810 | 12532368 |
| 24 | Don't Worry Darling                          |   2022 |      6.2 |   82116 | 10731256 |
| 25 | Ticket to Paradise                           |   2022 |      6.2 |   30892 | 14109724 |
| 26 | Valentino                                    |   1977 |      6.1 |    1967 |  0076868 |
| 27 | Lyle, Lyle, Crocodile                        |   2022 |      6.1 |    4956 | 14668630 |
| 28 | Serial (Bad) Weddings 3                      |   2021 |      6.1 |    1662 | 10405142 |
| 29 | Pil's Adventures                             |   2021 |      6.1 |     794 | 15091284 |
| 30 | Tad the Lost Explorer and the Emerald Tablet |   2022 |      5.9 |     832 | 14941698 |
| 31 | See for Me                                   |   2021 |      5.8 |    5011 | 11209212 |
| 32 | Paws of Fury: The Legend of Hank             |   2022 |      5.7 |    4407 |  4428398 |
| 33 | Mia and Me: The Hero of Centopia             |   2022 |      5.7 |     475 |  5790684 |
| 34 | Maria Into Life                              |   2022 |      5.6 |     185 | 14200996 |
| 35 | Last Seen Alive                              |   2022 |      5.6 |   18633 | 10242388 |
| 36 | Rabbit Academy                               |   2022 |      5.5 |     196 | 12631784 |
| 37 | Extinct                                      |   2021 |      5.5 |    2843 |  8241000 |
| 38 | School of Magical Animals                    |   2021 |      5.3 |     425 | 11455260 |
| 39 | The Roads Not Taken                          |   2020 |      5.2 |    2425 |  9411866 |
| 40 | Prey for the Devil                           |   2022 |      5.2 |    6522 |  9271672 |
| 41 | The Enforcer                                 |   2022 |      5.2 |    2253 | 14857730 |
| 42 | Strange World                                |   2022 |      4.9 |   10377 | 10298840 |
| 43 | My Sweet Monster                             |   2021 |      4.9 |     321 |  9572006 |
| 44 | Moonbound                                    |   2021 |      4.8 |     494 | 14534992 |
| 45 | Monster Family 2                             |   2021 |      4.8 |     849 | 15096796 |
| 46 | Detective Knight: Redemption                 |   2022 |      4.7 |     510 | 22394694 |
| 47 | Last Man Down                                |   2021 |      4.2 |   13317 | 12335692 |
| 48 | Detective Knight: Rogue                      |   2022 |      3.6 |     849 | 21435436 |
| 49 | Fortress: Sniper's Eye                       |   2022 |      2.9 |     840 | 14577304 |
```

