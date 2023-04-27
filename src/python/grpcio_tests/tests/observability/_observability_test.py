import unittest
import weakref
import sys
import logging
import os
import time
import random
import enum
import json
import logging
import multiprocessing
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from concurrent import futures

import grpc

from grpc_observability import observability

os.environ['OC_RESOURCE_TYPE'] = 'XUAN-TESTING'
os.environ[
    'OC_RESOURCE_LABELS'] = "instance_id=5501923375024409176,project_id=google.com:cloudtop-prod,zone=europe-west1-c"


_REQUEST = b'\x00\x00\x00'
_RESPONSE = b'\x00\x00\x00'

_UNARY_UNARY = '/test/UnaryUnary'
_UNARY_STREAM = '/test/UnaryStream'
_STREAM_UNARY = '/test/StreamUnary'
_STREAM_STREAM = '/test/StreamStream'
STREAM_LENGTH = 5

_SUBPROCESS_TIMEOUT_S = 80
_GDB_TIMEOUT_S = 60

_CLIENT_FORK_SCRIPT_TEMPLATE = """if True:
    import os
    from grpc._cython import cygrpc
    from tests.observability import methods

    from src.python.grpcio_tests.tests.observability import native_debug

    cygrpc._GRPC_ENABLE_FORK_SUPPORT = True
    os.environ['GRPC_POLL_STRATEGY'] = 'epoll1'
    os.environ['GRPC_ENABLE_FORK_SUPPORT'] = 'true'
    native_debug.install_failure_signal_handler()
    methods.run_test()
"""


def handle_unary_unary(request, servicer_context):
    return _RESPONSE


def handle_unary_stream(request, servicer_context):
    for _ in range(STREAM_LENGTH):
        yield _RESPONSE


def handle_stream_unary(request_iterator, servicer_context):
    return _RESPONSE


def handle_stream_stream(request_iterator, servicer_context):
    for request in request_iterator:
        yield _RESPONSE


class _MethodHandler(grpc.RpcMethodHandler):

    def __init__(self, request_streaming, response_streaming):
        self.request_streaming = request_streaming
        self.response_streaming = response_streaming
        self.request_deserializer = None
        self.response_serializer = None
        self.unary_unary = None
        self.unary_stream = None
        self.stream_unary = None
        self.stream_stream = None
        if self.request_streaming and self.response_streaming:
            self.stream_stream = lambda x, y: handle_stream_stream(x, y)
        elif self.request_streaming:
            self.stream_unary = lambda x, y: handle_stream_unary(x, y)
        elif self.response_streaming:
            self.unary_stream = lambda x, y: handle_unary_stream(x, y)
        else:
            self.unary_unary = lambda x, y: handle_unary_unary(x, y)


class _GenericHandler(grpc.GenericRpcHandler):

    def __init__(self):
        pass

    def service(self, handler_call_details):
        if handler_call_details.method == _UNARY_UNARY:
            return _MethodHandler(False, False)
        elif handler_call_details.method == _UNARY_STREAM:
            return _MethodHandler(False, True)
        elif handler_call_details.method == _STREAM_UNARY:
            return _MethodHandler(True, False)
        elif handler_call_details.method == _STREAM_STREAM:
            return _MethodHandler(True, True)
        else:
            return None

def _dump_streams(name, streams):
    assert len(streams) == 2
    for stream_name, stream in zip(("STDOUT", "STDERR"), streams):
        stream.seek(0)
        sys.stderr.write("{} {}:\n{}\n".format(name, stream_name,
                                               stream.read().decode("ascii")))
        stream.close()
    sys.stderr.flush()

class ObservabilityTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        sys.stderr.write("PY: tearing down test...\n")
        sys.stderr.flush()

    def t1est_sunny_day(self):
        script = _CLIENT_FORK_SCRIPT_TEMPLATE
        streams = tuple(tempfile.TemporaryFile() for _ in range(2))
        process = subprocess.Popen([sys.executable, '-c', script],
                                   stdout=streams[0],
                                   stderr=streams[1])
        try:
            process.wait(timeout=_SUBPROCESS_TIMEOUT_S)
            self.assertEqual(0, process.returncode)
        except subprocess.TimeoutExpired:
            self._print_backtraces(process.pid)
            process.kill()
            raise AssertionError("Parent process timed out.")
        finally:
            _dump_streams("Parent", streams)

    def test_sunny_day(self):
        sys.stderr.write("\nPY: trying to import grpc_observability\n")
        sys.stderr.flush()

        with observability.GCPOpenCensusObservability() as o11y:
            o11y.init()

            sys.stderr.write("PY: Creating server\n")
            sys.stderr.flush()
            self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            self._server.add_generic_rpc_handlers(
                (_GenericHandler(),))
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

            self.unary_unary_1_call()
            # self.unary_unary_2_calls()
            # self.stream_unary()
            # self.stream_stream()

            # sys.stderr.write("PY: stopping server...\n")
            # sys.stderr.flush()
            self._server.stop(0)
            # sys.stderr.write("PY: closing channel...\n")
            # sys.stderr.flush()
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

    def _print_backtraces(self, pid):
        cmd = [
            "gdb",
            "-ex",
            "set confirm off",
            "-ex",
            "echo attaching",
            "-ex",
            "attach {}".format(pid),
            "-ex",
            "echo print_backtrace",
            "-ex",
            "thread apply all bt",
            "-ex",
            "echo printed_backtrace",
            "-ex",
            "quit",
        ]
        streams = tuple(tempfile.TemporaryFile() for _ in range(2))
        sys.stderr.write("Invoking gdb\n")
        sys.stderr.flush()
        process = subprocess.Popen(cmd, stdout=streams[0], stderr=streams[1])
        try:
            process.wait(timeout=_GDB_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            sys.stderr.write("gdb stacktrace generation timed out.\n")
        finally:
            _dump_streams("gdb", streams)


if __name__ == "__main__":
    logging.basicConfig()
    unittest.main(verbosity=2)
