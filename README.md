# movie-rater
Help you find your movie for the weekend using IMDB rating. For example:



```python
import yes_planet
```


```python
movies = yes_planet.get_movies("Rishon LeZion")
```


```python
for movie in sorted(movies.values(), reverse=True)[:10]:
    print(movie)
```

    bohemian rhapsody: 8.4/10 (121628)
    a star is born: 8.2/10 (102817)
    harmony: 8.1/10 (24)
    shoplifters: 8.1/10 (4519)
    creed 2: 8.1/10 (5737)
    two tails: 8.1/10 (703)
    srohim: 8.1/10 (51)
    incredibles 2: 7.9/10 (139465)
    ralph breaks the internet: 7.7/10 (6799)
    instant family: 7.7/10 (2066)
    


```python

```
