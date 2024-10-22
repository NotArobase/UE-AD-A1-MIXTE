import grpc

import showtime_pb2
import showtime_pb2_grpc
from google.protobuf.empty_pb2 import Empty

def get_movie_by_id(stub,id):
    movie = stub.GetMoviesByDate(id)
    print(movie.date)

def get_movie_by_id2(stub,id):
    movie = stub.GetAllShowtimes(id)
    first = movie.schedule[0]
    print(first)

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        print("-------------- GetMovieByID --------------")
        date = showtime_pb2.Date(date ="20151130")
        empty = Empty()
        get_movie_by_id(stub, date)
        get_movie_by_id2(stub, empty)


    channel.close()

if __name__ == '__main__':
    run()
