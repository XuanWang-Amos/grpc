import unittest
import weakref
import sys
import logging
import os
import time
import random
from concurrent import futures

import grpc

from opencensus.common.transports import sync
from opencensus.trace import base_exporter, execution_context, samplers
from opencensus.trace.tracer import Tracer
from opencensus.ext.stackdriver import stats_exporter

from grpc_observability import observability

os.environ['OC_RESOURCE_TYPE'] = 'XUAN-TESTING'
os.environ[
    'OC_RESOURCE_LABELS'] = "instance_id=5501923375024409176,project_id=google.com:cloudtop-prod,zone=europe-west1-c"


class gRPCPrintExporter(base_exporter.Exporter):
    """Export the spans by printing them.
    :type transport: :class:`type`
    :param transport: Class for creating new transport objects. It should
                      extend from the base_exporter :class:`.Transport` type
                      and implement :meth:`.Transport.export`. Defaults to
                      :class:`.SyncTransport`. The other option is
                      :class:`.AsyncTransport`.
    """

    def __init__(self, transport=sync.SyncTransport):
        self.transport = transport(self)

    def emit(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to emit
        """

    def export(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to export
        """
        self.transport.export(span_datas)


class PrintStatsExporter():

    def __init__(self):
        pass

    def export_metrics(self, metrics):
        metrics = list(metrics)
        for metric in metrics:
            sys.stderr.write("PY: {metric}\n")
            sys.stderr.flush()
            print(metric)


_REQUEST = b'\x00\x00\x00'
_RESPONSE = b'\x00\x00\x00'

_UNARY_UNARY = '/test/UnaryUnary'
_UNARY_STREAM = '/test/UnaryStream'
_STREAM_UNARY = '/test/StreamUnary'
_STREAM_STREAM = '/test/StreamStream'
STREAM_LENGTH = 5


def handle_unary_unary(test, request, servicer_context):
    return _RESPONSE


def handle_unary_stream(test, request, servicer_context):
    for _ in range(STREAM_LENGTH):
        yield _RESPONSE


def handle_stream_unary(test, request_iterator, servicer_context):
    return _RESPONSE


def handle_stream_stream(test, request_iterator, servicer_context):
    for request in request_iterator:
        yield _RESPONSE


class _MethodHandler(grpc.RpcMethodHandler):

    def __init__(self, test, request_streaming, response_streaming):
        self.request_streaming = request_streaming
        self.response_streaming = response_streaming
        self.request_deserializer = None
        self.response_serializer = None
        self.unary_unary = None
        self.unary_stream = None
        self.stream_unary = None
        self.stream_stream = None
        if self.request_streaming and self.response_streaming:
            self.stream_stream = lambda x, y: handle_stream_stream(test, x, y)
        elif self.request_streaming:
            self.stream_unary = lambda x, y: handle_stream_unary(test, x, y)
        elif self.response_streaming:
            self.unary_stream = lambda x, y: handle_unary_stream(test, x, y)
        else:
            self.unary_unary = lambda x, y: handle_unary_unary(test, x, y)


class _GenericHandler(grpc.GenericRpcHandler):

    def __init__(self, test):
        self._test = test

    def service(self, handler_call_details):
        if handler_call_details.method == _UNARY_UNARY:
            return _MethodHandler(self._test, False, False)
        elif handler_call_details.method == _UNARY_STREAM:
            return _MethodHandler(self._test, False, True)
        elif handler_call_details.method == _STREAM_UNARY:
            return _MethodHandler(self._test, True, False)
        elif handler_call_details.method == _STREAM_STREAM:
            return _MethodHandler(self._test, True, True)
        else:
            return None


class ObservabilityTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sunny_day(self):
        with observability.GCPOpenCensusObservability() as o11y:
            o11y.init()

            self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            self._server.add_generic_rpc_handlers(
                (_GenericHandler(weakref.proxy(self)),))
            port = self._server.add_insecure_port('[::]:0')

            self._server.start()
            self._channel = grpc.insecure_channel('localhost:%d' % port)
            self.unary_unary_1_call()
            # self.unary_unary_2_calls()
            # self.stream_unary()
            # self.stream_stream()

            self._server.stop(0)
            self._channel.close()

    def unary_unary_1_call(self):
        multi_callable = self._channel.unary_unary(_UNARY_UNARY)
        unused_response, call = multi_callable.with_call(_REQUEST)


    def unary_unary_2_calls(self):
        multi_callable = self._channel.unary_unary(_UNARY_UNARY)
        unused_response, call = multi_callable.with_call(_REQUEST)
        unused_response, call = multi_callable.with_call(_REQUEST)


    def stream_unary(self):
        multi_callable = self._channel.stream_unary(_STREAM_UNARY)
        unused_response, call = multi_callable.with_call(
            iter([_REQUEST] * STREAM_LENGTH))

    def stream_stream(self):
        multi_callable = self._channel.stream_stream(_STREAM_STREAM)
        call = multi_callable(iter([_REQUEST] * STREAM_LENGTH))
        for _ in call:
            pass


if __name__ == "__main__":
    logging.basicConfig()
    unittest.main(verbosity=2)
