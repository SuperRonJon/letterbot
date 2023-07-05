import tmdbsimple as tmdb
from dateutil.parser import parse
from secret import tmdb_key

tmdb.API_KEY = tmdb_key

def get_info_for_search(query):
    search = tmdb.Search()
    response = search.movie(query=query)
    if len(search.results) == 0:
        return None
    first_id = search.results[0]['id']
    try:
        movie = tmdb.Movies(first_id)
    except:
        return None
    response = movie.info()
    date = parse(movie.release_date)
    date_string = date.strftime('%B %d %Y')
    genres_string = ""
    for genre in movie.genres:
        if genres_string:
            genres_string += " - "
        genres_string += genre['name']
    response = movie.watch_providers()
    provider_string = ""
    try:
        providers = movie.results["US"]["flatrate"]
        for provider in providers:
            if provider_string:
                provider_string += " - "
            provider_string += provider["provider_name"]
    except KeyError:
        print("no streaming providers")
        provider_string = "None"
    result = {
        "title": movie.title,
        "description": movie.overview,
        "imdb_link": "https://www.imdb.com/title/" + movie.imdb_id,
        "release_date": date_string,
        "genres": genres_string,
        "poster_link": "http://image.tmdb.org/t/p/original/" + movie.poster_path,
        "providers": provider_string
    }
    return result