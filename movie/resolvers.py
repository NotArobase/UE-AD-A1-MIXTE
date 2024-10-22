import json

def movie_with_id(_,info,_id):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie

def movie_by_title(_,info,title):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['title'] == title:
                return movie

def update_movie_rate(_,info,_id,_rate):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        result = [actor for actor in actors['actors'] if movie['id'] in actor['films']]
        return result

def add_movie(_, info, title, director, rating, actors):
    
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies_data = json.load(rfile)

    with open('{}/data/actors.json'.format("."), "r") as afile:
        actors_data = json.load(afile)

    new_movie_id =str(len(movies_data['movies']) + 1)

    new_movie = {
        "id": new_movie_id,  
        "title": title,
        "director": director,
        "rating": rating,
    }

    movies_data['movies'].append(new_movie)

    with open('{}/data/movies.json'.format("."), "w") as wMovies:
        json.dump(movies_data, wMovies, indent=4)

    movie_actors = []
    for actor_input in actors:
        existing_actor = next((actor for actor in actors_data['actors'] if actor['id'] == actor_input['id']), None)

        if existing_actor:
            movie_actors.append(existing_actor)
        else:
            new_actor = {
                "id": actor_input['id'],
                "firstname": actor_input['firstname'],
                "lastname": actor_input['lastname'],
                "birthyear": actor_input['birthyear'],
                "films": [new_movie_id]
            }
            movie_actors.append(new_actor)
            actors_data['actors'].append(new_actor) 

    with open('{}/data/actors.json'.format("."), "w") as wActors:
        json.dump(actors_data, wActors, indent=4)

    return new_movie

def delete_movie(_, info, _id):
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies_data = json.load(rfile)

    deleted_movie = None
    updated_movies = [movie for movie in movies_data['movies'] if movie['id'] != _id]
    
    for movie in movies_data['movies']:
        if movie['id'] == _id:
            deleted_movie = movie
            break

    if not deleted_movie:
        raise Exception(f"Movie with id {_id} not found")

    movies_data['movies'] = updated_movies

    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(movies_data, wfile, indent=4)

    return deleted_movie