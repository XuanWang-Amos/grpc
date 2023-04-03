import unittest
import weakref
import sys
import logging
import os
import time
import random

import grpc

from tests.unit import test_common

from opencensus.common.transports import sync
from opencensus.trace import base_exporter, execution_context, samplers
from opencensus.trace.tracer import Tracer
from opencensus.ext.stackdriver import stats_exporter

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
        sys.stderr.write(f"gRPCPrintExporter Exported span: {span_datas}\n")
        sys.stderr.flush()

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
    for request in request_iterator:
        pass
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
        sys.stderr.write("PY: tearing down test...\n")
        sys.stderr.flush()

    def tes1t_tracing(self):
        sampler = samplers.ProbabilitySampler(rate=1)
        tracer = Tracer(sampler=sampler)
        with tracer.span(name="doingWork") as span:
            for i in range(10):
                pass

    def tes1t_metrics(self):
        from opencensus.metrics import transport

        from opencensus.stats import aggregation as aggregation_module
        from opencensus.stats import measure as measure_module
        from opencensus.stats import stats as stats_module
        from opencensus.stats import view as view_module
        from opencensus.tags import tag_map as tag_map_module

        # The stats recorder
        stats = stats_module.stats
        view_manager = stats.view_manager
        stats_recorder = stats.stats_recorder

        m_latency_ms = measure_module.MeasureFloat(
            "task_latency", "The task latency in milliseconds", "ms")
        view_name = "test_metrics_latency_distribution"
        latency_view = view_module.View(
            view_name,  # name
            "The distribution of the task latencies",  # description
            [],  # columns ('~opencensus.tags.tag_key.TagKey')
            m_latency_ms,  # measure ('~opencensus.stats.measure.Measure')
            # Latency in buckets: [>=0ms, >=100ms, >=200ms, >=400ms, >=1s, >=2s, >=4s]
            # aggregation ('~opencensus.stats.aggregation.BaseAggregation')
            aggregation_module.DistributionAggregation(
                [100.0, 200.0, 400.0, 1000.0, 2000.0, 4000.0]))

        # print_exporter = PrintStatsExporter()
        # exporter = transport.get_exporter_thread([stats_module.stats], print_exporter, interval=None)

        exporter = stats_exporter.new_stats_exporter(interval=10)
        print('Exporting stats to project "{}"'.format(
            exporter.options.project_id))

        view_manager.register_exporter(exporter)
        view_manager.register_view(latency_view)
        mmap = stats_recorder.new_measurement_map()
        tmap = tag_map_module.TagMap()

        for i in range(5):
            ms = random.random() * 5 * 1000
            # print("Latency {0}:{1}".format(i, ms))
            mmap.measure_float_put(m_latency_ms, ms)
            mmap.record(tmap)
            time.sleep(1)

        print("Done recording metrics")
        # Keep the thread alive long enough for the exporter to export at least
        # once.
        time.sleep(15)

    def test_sunny_day(self):
        sys.stderr.write("\nPY: trying to import grpc_observability\n")
        sys.stderr.flush()
        from grpc_observability import observability

        with observability.Observability() as o11y:

            o11y.init()

            sys.stderr.write("PY: Creating server\n")
            sys.stderr.flush()
            self._server = test_common.test_server()
            self._server.add_generic_rpc_handlers(
                (_GenericHandler(weakref.proxy(self)),))
            port = self._server.add_insecure_port('[::]:0')

            sys.stderr.write("PY: Starting server\n")
            sys.stderr.flush()
            self._server.start()
            sys.stderr.write("PY: Server started\n")
            sys.stderr.flush()

            sys.stderr.write(
                "PY: Start Creating Channel using grpc.insecure_channel\n")
            sys.stderr.flush()
            self._channel = grpc.insecure_channel('localhost:%d' % port)
            # self._channel = grpc.insecure_channel('localhost:55555')
            sys.stderr.write("PY: created self._channel\n")
            sys.stderr.flush()

            # self.unary_unary_1_call()
            # self.unary_unary_2_calls()
            self.stream_unary()
            # self.stream_stream()

            sys.stderr.write("PY: stopping server...\n")
            sys.stderr.flush()
            self._server.stop(0)
            sys.stderr.write("PY: closing channel...\n")
            sys.stderr.flush()
            self._channel.close()

    def unary_unary_1_call(self):
        sys.stderr.write("PY: creating multi_callable...\n")
        sys.stderr.flush()
        multi_callable = self._channel.unary_unary(_UNARY_UNARY)

        sys.stderr.write("PY: Invoking 1st UnaryUnary RPC...\n")
        sys.stderr.flush()
        unused_response, call = multi_callable.with_call(_REQUEST)
        sys.stderr.write(
            f"PY: multi_callable responde with code {call.code()}\n\n\n\n\n")
        sys.stderr.flush()

    def unary_unary_2_calls(self):
        sys.stderr.write("PY: creating multi_callable...\n")
        sys.stderr.flush()
        multi_callable = self._channel.unary_unary(_UNARY_UNARY)

        sys.stderr.write("PY: Invoking 1st UnaryUnary RPC...\n")
        sys.stderr.flush()
        unused_response, call = multi_callable.with_call(_REQUEST)
        sys.stderr.write(
            f"PY: multi_callable responde with code {call.code()}\n\n\n\n\n")
        sys.stderr.flush()

        sys.stderr.write("PY: Invoking 2nd UnaryUnary RPC...\n")
        sys.stderr.flush()
        unused_response, call = multi_callable.with_call(_REQUEST)
        sys.stderr.write(
            f"PY: multi_callable responde with code {call.code()}\n")
        sys.stderr.flush()

    def stream_unary(self):
        sys.stderr.write("PY: creating multi_callable...\n")
        sys.stderr.flush()
        multi_callable = self._channel.stream_unary(_STREAM_UNARY)

        sys.stderr.write("PY: Invoking 1st StreamUnary RPC...\n")
        sys.stderr.flush()
        unused_response, call = multi_callable.with_call(
            iter([_REQUEST] * STREAM_LENGTH))
        sys.stderr.write(
            f"PY: multi_callable responde with code {call.code()}\n\n\n\n\n")
        sys.stderr.flush()

    def stream_stream(self):
        sys.stderr.write("PY: creating multi_callable...\n")
        sys.stderr.flush()
        multi_callable = self._channel.stream_stream(_STREAM_STREAM)
        sys.stderr.write("PY: Invoking 1st StreamUnary RPC...\n")
        sys.stderr.flush()
        call = multi_callable(iter([_REQUEST] * STREAM_LENGTH))
        for _ in call:
            pass
        sys.stderr.write(
            f"PY: multi_callable responde with code {call.code()}\n\n\n\n\n")
        sys.stderr.flush()


if __name__ == "__main__":
    logging.basicConfig()
    unittest.main(verbosity=2)
