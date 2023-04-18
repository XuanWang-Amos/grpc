import sys
import time
import os
import codecs

from typing import Optional

from libcpp.cast cimport static_cast
from libc.stdio cimport printf

import grpc

cdef const char* CLIENT_CALL_TRACER = "gcp_opencensus_client_call_tracer"
cdef const char* SERVER_CALL_TRACER_FACTORY = "gcp_opencensus_server_call_tracer_factory"

def set_server_call_tracer_factory() -> None:
  observability = get_grpc_observability()
  capsule = observability.create_server_call_tracer_factory()
  capsule_ptr = cpython.PyCapsule_GetPointer(capsule, SERVER_CALL_TRACER_FACTORY)
  grpc_register_server_call_tracer_factory(capsule_ptr)


def set_context_from_server_call_tracer(RequestCallEvent event) -> None:
  pass


def record_rpc_latency(state) -> None:
  observability = get_grpc_observability()
  if not (observability and observability._stats_enabled()):
    return
  rpc_latency = state.rpc_end_time - state.rpc_start_time
  rpc_latency_ms = rpc_latency.total_seconds() * 1000
  observability.record_rpc_latency(state.method, rpc_latency_ms, state.code)


def get_grpc_observability() -> Optional[grpc.GrpcObservability]:
  return getattr(grpc, '_grpc_observability', None)


cdef void mapbe_set_client_call_tracer_on_call(_CallState call_state, bytes method):
  observability = get_grpc_observability()
  if not (observability and observability._observability_enabled()):
    return
  capsule = observability.create_client_call_tracer_capsule(method)
  capsule_ptr = cpython.PyCapsule_GetPointer(capsule, CLIENT_CALL_TRACER)
  grpc_call_set_call_tracer(call_state.c_call, capsule_ptr)
  call_state.call_tracer_capsule = capsule