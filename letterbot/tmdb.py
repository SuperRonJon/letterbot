import tmdbsimple as tmdb
from dateutil.parser import parse
from secret import tmdb_key

tmdb.API_KEY = tmdb_key

def get_info_for_search(query):
    # Search for movie based on query
    search = tmdb.Search()
    response = search.movie(query=query)
    if len(search.results) == 0:
        return None
    first_id = search.results[0]['id']
    try:
        movie = tmdb.Movies(first_id)
    except:
        return None
    
    # If movie is found get details
    response = movie.info()
    date = parse(movie.release_date)
    date_string = date.strftime('%B %d %Y')

    # Parse genres
    genres_string = stringify_objects(movie.genres, "name", " - ")

    # Get streaming providers
    response = movie.watch_providers()
    try:
        no_channel_providers = list(filter(is_service, movie.results["US"]["flatrate"]))
        provider_string = stringify_objects(no_channel_providers, "provider_name", " - ")
    except Exception:
        provider_string = "None"
    
    # Get director
    response = movie.credits()
    directors = filter(is_director, movie.crew)
    director_string = stringify_objects(directors, "name", ", ")

    # Get top cast
    top_cast = movie.cast[:3]
    cast_string = stringify_objects(top_cast, "name", ", ")

    result = {
        "title": movie.title,
        "description": movie.overview,
        "director": director_string,
        "cast": cast_string,
        "imdb_link": "https://www.imdb.com/title/" + movie.imdb_id,
        "release_date": date_string,
        "genres": genres_string,
        "poster_link": "http://image.tmdb.org/t/p/original/" + movie.poster_path,
        "providers": provider_string
    }
    return result

def is_director(p):
    return p["job"] == "Director"

def stringify_objects(objects, key, delimiter):
    result = ""
    for object in objects:
        if result:
            result += delimiter
        result += object[key]
    return result

def is_service(provider):
    return not provider["provider_name"].endswith("Channel")
