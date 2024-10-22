import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc
import json

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetAllBookings(self, request, context):
        booking_list = [
            booking_pb2.UserBooking(
                userid=booking['userid'],
                dates=[  # Changed from 'movies' to 'dates'
                    booking_pb2.BookingData(
                        date=bookingDate['date'],
                        movies=bookingDate['movies']
                    ) for bookingDate in booking['dates']
                ]
            )
            for booking in self.db
        ]
        return booking_pb2.AllBookings(bookings=booking_list)

    def GetBookingsForUser(self, request, context):
        for booking in self.db:
            if booking['userid'] == request.id:
                return booking_pb2.UserBooking(
                    userid=booking['userid'],
                    dates=[  # Changed from 'movies' to 'dates'
                        booking_pb2.BookingData(
                            date=bookingDate['date'],
                            movies=bookingDate['movies']
                        ) for bookingDate in booking['dates']
                    ]
                )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('User ID not found')
        return booking_pb2.UserBooking(userid="", dates=[])

    def AddBooking(self, request, context):
        showtime = get_movies_for_date(request.date)
        if not showtime or not showtime.movies:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('No movies available for the specified date')
            return booking_pb2.UserBooking(userid="", dates=[])  
        
        if request.movieid not in showtime.movies:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('The specified movie is not scheduled for this date')
            return booking_pb2.UserBooking(userid="", dates=[])


        user_booking = None
        for booking in self.db:
            if booking['userid'] == request.userid:
                user_booking = booking
                break
        
        if user_booking is None:
            new_booking = {
                'userid': request.userid,
                'dates': [{'date': request.date, 'movies': [request.movieid]}]  # Changed to handle single movieid
            }
            self.db.append(new_booking)

            with open('./data/bookings.json', 'w') as jsf:
                json.dump({"bookings": self.db}, jsf)

            return booking_pb2.UserBooking(
                userid=new_booking['userid'],
                dates=[
                    booking_pb2.BookingData(
                        date=booking_date['date'],
                        movies=booking_date['movies']
                    ) for booking_date in new_booking['dates']
                ]
            )
        else:
            date_entry = next((d for d in user_booking['dates'] if d['date'] == request.date), None)
            if date_entry:
                if request.movieid not in date_entry['movies']:
                    date_entry['movies'].append(request.movieid)  # Append single movieid to existing date's movies
            else:
                user_booking['dates'].append({'date': request.date, 'movies': [request.movieid]})  # Add new date with movieid

            with open('./data/bookings.json', 'w') as jsf:
                json.dump({"bookings": self.db}, jsf)

            return booking_pb2.UserBooking(
                userid=request.userid,
                dates=[
                    booking_pb2.BookingData(
                        date=booking_date['date'],
                        movies=booking_date['movies']
                    ) for booking_date in user_booking['dates']
                ]
            )

def get_movies_for_date(date):
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        dateShowtime = showtime_pb2.Date(date=date)
        return stub.GetMoviesByDate(dateShowtime)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('0.0.0.0:3001')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
