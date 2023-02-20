import pprint

movie_database = [
 {'title': 'Furious 7', 'genre': 'Action', 'showtimes': ['15:00', '17:00', '19:00']},
 {'title': 'Movie 2', 'genre': 'Comedy', 'showtimes': ['14:00', '16:00', '18:00']},
 {'title': 'Avatar: The Way of Water', 'genre': 'Action', 'showtimes': ['8:00', ' 11:00', ' 13:00', ' 16:00', ' 19:00']}
]

def add_movie(movie_database: list) -> list:
    """Adds a defined movie to the provided movie database, returning the result."""
    title: str = input("What's the film's title? ")
    genre: str = input("What genre is the film in? ").capitalize()
    showtimes: list = input("Input the showtimes of the film in 24hr time, seperated by commas (,): ").strip().split(",")

    movie_database.append(
        {'title': title, 'genre': genre, 'showtimes': showtimes}
    )
    return movie_database

def find_movies_by_genre(movie_database: list, genre: str) -> list:
    """Search the movie database by genre."""
    filtered_movies = []
    for movie in movie_database:
        if genre == movie['genre']:
            filtered_movies.append(movie)
    return filtered_movies

def _time_to_minutes(time: str) -> int:
    """Converts a time to the number of minutes.

    Args:
        time (str): A time in the 24hr format (hours:minutes e.g. 13:15)

    Returns:
        int: The number of minutes.
    """
    values = time.split(":")
    values = [int(value) for value in values]
    if len(values) != 2:
        raise ValueError("The timestamp is invalid.")
    return values[1] + values[0]*60

def find_earliest_and_latest_showtime(movie_database: list, title: str) -> int:
    movie = {}
    for searchedmovie in movie_database:
        if searchedmovie['title'] == title:
            movie = searchedmovie
            
            break
    times = [_time_to_minutes(time) for time in movie['showtimes']]
    print(times)

    first_time = movie['showtimes'][times.index(min(times))]
    last_time = movie['showtimes'][times.index(max(times))]
    return first_time, last_time

# movie_database = add_movie(movie_database)
# print(find_earliest_and_latest_showtime(movie_database, 'Avatar: The Way of Water'))
pprint.pprint(find_movies_by_genre(movie_database, input("Choose a genre to search: ").capitalize()))
print(movie_database)
    
# print(time_to_minutes("2:00"))