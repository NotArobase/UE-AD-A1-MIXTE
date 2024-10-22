# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

import grpc
import booking_pb2
import booking_pb2_grpc
# import movie_pb2
# import movie_pb2_grpc

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

BOOKING_SERVICE_URL = "localhost:3001"
MOVIE_SERVICE_URL = "http://localhost:3000/graphql"

PORT = 3003
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_all_users():
    return jsonify(users), 200

@app.route("/users/<string:userid>/bookings", methods=['GET'])
def get_user_bookings(userid):
    user = next((u for u in users if u['id'] == userid), None)
    if not user:
        return make_response(jsonify({"error": "User ID not found"}), 404)

    stub, channel = get_booking_stub()
    try:
        response = stub.GetBookingsForUser(booking_pb2.UserID(id=userid))
        if response.userid:
            return jsonify({
                "userid": response.userid,
                "dates": [
                    {"date": booking.date, "movies": list(booking.movies)} 
                    for booking in response.dates  # Changed from 'response.movies' to 'response.dates'
                ]
            }), 200
        else:
            return make_response(jsonify({"error": "No bookings found"}), 404)
    except grpc.RpcError as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        channel.close()

@app.route("/users/<string:userid>/bookings/<string:date>", methods=['GET'])
def get_user_bookings_by_date(userid,date):
    user = next((u for u in users if u['id'] == userid), None)
    if not user:
        return make_response(jsonify({"error": "User ID not found"}), 404)

    # gRPC request to BookingServicer's GetBookingsForUser
    stub, channel = get_booking_stub()
    try:
        response = stub.GetBookingsForUser(booking_pb2.UserID(id=userid))
        for date_item in response.dates:
            if date_item.date == date:
                return jsonify({
                    "userid": userid,
                    "date": date_item.date,
                    "movies": list(date_item.movies)
                }), 200
        return jsonify({"error": "No bookings found for the specified date"}), 404
    except grpc.RpcError as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        channel.close()

@app.route("/users/<string:userid>/movies", methods=['GET'])
def get_user_movies(userid):
    user = next((u for u in users if u['id'] == userid), None)
    if not user:
        return make_response(jsonify({"error": "User ID not found"}), 404)

    # gRPC request to BookingServicer's GetBookingsForUser
    stub, channel = get_booking_stub()
    try:
        response = stub.GetBookingsForUser(booking_pb2.UserID(id=userid))
        if not response.dates:
            return make_response(jsonify({"error": "No bookings found"}), 404)

        movie_ids = []
        for date_item in response.dates:
            movie_ids.extend(date_item.movies)

        movies_details = []
        for movieid in movie_ids:
            # Using GraphQL query to fetch movie details
            query = '''
            query getMovieById($id: String!) {
                movie_with_id(_id: $id) {
                    id
                    title
                    director
                    rating
                    actors {
                        id
                        firstname
                        lastname
                        birthyear
                    }
                }
            }
            '''
            variables = {"id": movieid}
            movie_response = requests.post(MOVIE_SERVICE_URL, json={'query': query, 'variables': variables})

            if movie_response.status_code == 200:
                movie_data = movie_response.json().get('data', {}).get('movie_with_id')
                if movie_data:
                    movies_details.append(movie_data)

        if not movies_details:
            return make_response(jsonify({"error": "No movies found for the user's bookings"}), 404)

        return jsonify(movies_details), 200
    except grpc.RpcError as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        channel.close()


@app.route("/users/<string:userid>/bookings", methods=['POST'])
def add_user_booking(userid):
    req_data = request.get_json()
    if not req_data or "date" not in req_data or "movieid" not in req_data:
        return make_response(jsonify({"error": "Invalid input"}), 400)

    # gRPC request to BookingServicer's AddBooking
    stub, channel = get_booking_stub()
    try:
        response = stub.AddBooking(booking_pb2.BookingRequest(
            userid=userid,
            date=req_data["date"],
            movieid=req_data["movieid"]
        ))
        if response.userid:
            return jsonify({
                "movieid": req_data["movieid"],  
                "date": req_data["date"]  
            }), 200
        else:
            return make_response(jsonify({"error": response.message}), 404)
    except grpc.RpcError as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        channel.close()
    

@app.route("/users/<string:userid>/bookingsbytitle", methods=['POST'])
def add_user_booking_by_title(userid):
    req_data = request.get_json()

    if not req_data or "date" not in req_data or "title" not in req_data:
        return make_response(jsonify({"error": "Invalid input"}), 400)

    title = req_data["title"]
    date = req_data["date"]

    query = '''
    query getMovieByTitle($title: String!) {
        movie_by_title(_id: $title) {
            id
            title
        }
    }
    '''
    variables = {"title": title}
    movie_response = requests.post(MOVIE_SERVICE_URL, json={'query': query, 'variables': variables})

    if movie_response.status_code == 200:
            movie_data = movie_response.json().get('data', {}).get('movie_by_title')
            if movie_data:
                movieid = movie_response.json().get('id')
                payload = {
                    "movieid": movieid,
                    "date": date
                }
            else:
                return make_response(jsonify({"error": "Movie title not found"}), 404)
    else:
        return make_response(jsonify({"error": "An error occurred while retrieving the movie"}), 500)

    booking_url = f"{BOOKING_SERVICE_URL}/bookings/{userid}"
    booking_response = requests.post(booking_url, json=payload)

    if booking_response.status_code == 200:
        return jsonify(booking_response.json()), 200
    elif booking_response.status_code == 404:
        return make_response(jsonify({"error": "Movie or showtime not found"}), 404)
    elif booking_response.status_code == 409:
        return make_response(jsonify({"error": "Booking already exists"}), 409)
    else:
        return make_response(jsonify({"error": "An error occurred while processing the booking"}), 500)
    

@app.route("/users/movies/<string:movieid>", methods=['GET'])
def get_movie_by_id(movieid):
    query = '''
    query getMovieById($id: String!) {
        movie_with_id(_id: $id) {
            id
            title
            director
            rating
            actors {
                id
                firstname
                lastname
                birthyear
            }
        }
    }
    '''
    variables = {"id": movieid}
    response = requests.post(MOVIE_SERVICE_URL, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        movie_data = response.json().get('data', {}).get('movie_with_id')
        if movie_data:
            return jsonify(movie_data), 200
        else:
            return make_response(jsonify({"error": "Movie ID not found"}), 404)
    else:
        return make_response(jsonify({"error": "An error occurred while retrieving the movie"}), 500)


@app.route("/users/moviesbytitle", methods=['GET'])
def get_movie_by_title():
    if request.args and 'title' in request.args:
        title = request.args['title']

        # GraphQL query to fetch movie by title
        query = '''
        query getMovieByTitle($title: String!) {
            movie_by_title(title: $title) {
                id
                title
                director
                rating
                actors {
                    id
                    firstname
                    lastname
                    birthyear
                }
            }
        }
        '''
        variables = {"title": title}
        movie_response = requests.post(MOVIE_SERVICE_URL, json={'query': query, 'variables': variables})


        if movie_response.status_code == 200:
            movie_data = movie_response.json().get('data', {}).get('movie_by_title')
            if movie_data:
                return jsonify(movie_data), 200
            else:
                return make_response(jsonify({"error": "Movie title not found"}), 404)
        else:
            return make_response(jsonify({"error": "An error occurred while retrieving the movie"}), 500)
    return make_response(jsonify({"error": "Invalid input"}), 400)

@app.route("/users/movies/<string:movieid>", methods=['POST'])
def add_movie(movieid):
    req_data = request.get_json()

    if not req_data or "title" not in req_data or "rating" not in req_data:
        return make_response(jsonify({"error": "Invalid input"}), 400)

    mutation = '''
    mutation addMovie($title: String!, $director: String!, $rating: Float!, $actors: [ActorInput]) {
        add_movie(title: $title, director: $director, rating: $rating, actors: $actors) {
            id
            title
            rating
        }
    }
    '''
    variables = {
        "title": req_data["title"],
        "director": req_data["director"],
        "rating": req_data["rating"],
        "actors": req_data.get("actors", [])
    }
    response = requests.post(MOVIE_SERVICE_URL, json={'query': mutation, 'variables': variables})

    if response.status_code == 200:
        return jsonify(response.json().get('data', {}).get('add_movie')), 200
    else:
        return make_response(jsonify({"error": "An error occurred while adding the movie"}), 500)


@app.route("/users/movies/<string:movieid>/rate/<string:rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    mutation = '''
    mutation updateMovieRating($id: String!, $rate: Float!) {
        update_movie_rate(_id: $id, _rate: $rate) {
            id
            title
            rating
        }
    }
    '''
    variables = {"id": movieid, "rate": float(rate)}
    response = requests.post(MOVIE_SERVICE_URL, json={'query': mutation, 'variables': variables})

    if response.status_code == 200:
        return jsonify(response.json().get('data', {}).get('update_movie_rate')), 200
    else:
        return make_response(jsonify({"error": "An error occurred while updating the rating"}), 500)


@app.route("/users/movies/<string:movieid>", methods=['DELETE'])
def delete_movie(movieid):
    mutation = '''
    mutation deleteMovie($id: String!) {
        delete_movie(_id: $id) {
            id
            title
        }
    }
    '''
    variables = {"id": movieid}
    response = requests.post(MOVIE_SERVICE_URL, json={'query': mutation, 'variables': variables})

    if response.status_code == 200:
        delete_movie_data = response.json().get('data', {}).get('delete_movie')

        if delete_movie_data is None:
            # Movie was not found
            return make_response(jsonify({"error": f"Cannot find the movie with ID {movieid}"}), 404)
        else:
            # Movie was successfully deleted
            return jsonify(delete_movie_data), 200
    else:
        return make_response(jsonify({"error": "An error occurred while deleting the movie"}), 500)

def get_booking_stub():
    channel = grpc.insecure_channel(BOOKING_SERVICE_URL)
    stub = booking_pb2_grpc.BookingStub(channel)
    return stub, channel

if __name__ == "__main__":
    print(f"Server running on port {PORT}")
    app.run(host=HOST, port=PORT)

