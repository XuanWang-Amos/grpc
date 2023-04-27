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

_CHILD_FINISH_TIMEOUT_S = 10
_GDB_TIMEOUT_S = 60

class _ChildProcess(object):

    def __init__(self, task, args=None):
        if args is None:
            args = ()
        self._exceptions = multiprocessing.Queue()
        self._stdout_path = tempfile.mkstemp()[1]
        self._stderr_path = tempfile.mkstemp()[1]
        self._child_pid = None
        self._rc = None
        self._args = args

        self._task = task

    def _child_main(self):
        import faulthandler
        faulthandler.enable(all_threads=True)

        try:
            self._task(*self._args)
        except grpc.RpcError as rpc_error:
            traceback.print_exc()
            self._exceptions.put('RpcError: %s' % rpc_error)
        except Exception as e:  # pylint: disable=broad-except
            traceback.print_exc()
            self._exceptions.put(e)
        sys.exit(0)

    def _orchestrate_child_gdb(self):
        cmd = [
            "gdb",
            "-ex",
            "set confirm off",
            "-ex",
            "attach {}".format(os.getpid()),
            "-ex",
            "set follow-fork-mode child",
            "-ex",
            "continue",
            "-ex",
            "bt",
        ]
        streams = tuple(tempfile.TemporaryFile() for _ in range(2))
        sys.stderr.write("Invoking gdb\n")
        sys.stderr.flush()
        process = subprocess.Popen(cmd, stdout=sys.stderr, stderr=sys.stderr)
        time.sleep(5)

    def start(self):
        # NOTE: Try uncommenting the following line if the child is segfaulting.
        # self._orchestrate_child_gdb()
        ret = os.fork()
        if ret == 0:
            self._child_main()
        else:
            self._child_pid = ret

    def wait(self, timeout):
        total = 0.0
        wait_interval = 1.0
        while total < timeout:
            ret, termination = os.waitpid(self._child_pid, os.WNOHANG)
            if ret == self._child_pid:
                self._rc = termination
                return True
            time.sleep(wait_interval)
            total += wait_interval
        else:
            return False

    def _print_backtraces(self):
        cmd = [
            "gdb",
            "-ex",
            "set confirm off",
            "-ex",
            "echo attaching",
            "-ex",
            "attach {}".format(self._child_pid),
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
            for stream_name, stream in zip(("STDOUT", "STDERR"), streams):
                stream.seek(0)
                sys.stderr.write("gdb {}:\n{}\n".format(
                    stream_name,
                    stream.read().decode("ascii")))
                stream.close()
            sys.stderr.flush()

    def finish(self):
        terminated = self.wait(_CHILD_FINISH_TIMEOUT_S)
        sys.stderr.write("Exit code: {}\n".format(self._rc))
        if not terminated:
            self._print_backtraces()
            raise RuntimeError('Child process did not terminate')
        if self._rc != 0:
            raise ValueError('Child process failed with exitcode %d' % self._rc)
        try:
            exception = self._exceptions.get(block=False)
            raise ValueError('Child process failed: "%s": "%s"' %
                             (repr(exception), exception))
        except queue.Empty:
            pass


_REQUEST = b'\x00\x00\x00'
_RESPONSE = b'\x00\x00\x00'

_UNARY_UNARY = '/test/UnaryUnary'
_UNARY_STREAM = '/test/UnaryStream'
_STREAM_UNARY = '/test/StreamUnary'
_STREAM_STREAM = '/test/StreamStream'
STREAM_LENGTH = 5


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

def run_test():
    def child_target():
        with observability.GCPOpenCensusObservability() as o11y:
            o11y.init()

            sys.stderr.write("PY: Creating server\n"); sys.stderr.flush()
            _server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            _server.add_generic_rpc_handlers(
                (_GenericHandler(),))
            port = _server.add_insecure_port('[::]:0')

            sys.stderr.write("PY: Starting server\n"); sys.stderr.flush()
            _server.start()
            sys.stderr.write("PY: Server started\n"); sys.stderr.flush()

            sys.stderr.write("PY: Start Creating Channel using grpc.insecure_channel\n");sys.stderr.flush()
            _channel = grpc.insecure_channel('localhost:%d' % port)
            sys.stderr.write("PY: created self._channel\n"); sys.stderr.flush()

            sys.stderr.write("PY: creating multi_callable...\n");sys.stderr.flush()
            multi_callable = _channel.unary_unary(_UNARY_UNARY)

            sys.stderr.write("PY: Invoking 1st UnaryUnary RPC...\n"); sys.stderr.flush()
            unused_response, call = multi_callable.with_call(_REQUEST)
            sys.stderr.write(f"PY: multi_callable responde with code {call.code()}\n\n\n\n\n"); sys.stderr.flush()

            sys.stderr.write("PY: stopping server...\n"); sys.stderr.flush()
            _server.stop(0)
            sys.stderr.write("PY: closing channel...\n"); sys.stderr.flush()
            _channel.close()

    child_process = _ChildProcess(child_target)
    child_process.start()
    child_process.finish()
