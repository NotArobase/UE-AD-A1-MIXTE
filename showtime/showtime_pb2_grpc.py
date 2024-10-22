# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import showtime_pb2 as showtime__pb2

GRPC_GENERATED_VERSION = '1.66.1'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in showtime_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ShowtimeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAllShowtimes = channel.unary_unary(
                '/Showtime/GetAllShowtimes',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=showtime__pb2.AllShowtimeData.FromString,
                _registered_method=True)
        self.GetMoviesByDate = channel.unary_unary(
                '/Showtime/GetMoviesByDate',
                request_serializer=showtime__pb2.Date.SerializeToString,
                response_deserializer=showtime__pb2.ShowtimeData.FromString,
                _registered_method=True)


class ShowtimeServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetAllShowtimes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMoviesByDate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ShowtimeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetAllShowtimes': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAllShowtimes,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=showtime__pb2.AllShowtimeData.SerializeToString,
            ),
            'GetMoviesByDate': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMoviesByDate,
                    request_deserializer=showtime__pb2.Date.FromString,
                    response_serializer=showtime__pb2.ShowtimeData.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Showtime', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('Showtime', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Showtime(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetAllShowtimes(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Showtime/GetAllShowtimes',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            showtime__pb2.AllShowtimeData.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetMoviesByDate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Showtime/GetMoviesByDate',
            showtime__pb2.Date.SerializeToString,
            showtime__pb2.ShowtimeData.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
