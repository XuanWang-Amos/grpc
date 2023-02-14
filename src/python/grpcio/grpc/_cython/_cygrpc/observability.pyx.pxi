import sys
import time
import os
import codecs
from libcpp.cast cimport static_cast
from cpython.ref cimport PyObject
from libc.stdio cimport printf

from grpc import _observability

cdef const char* CLIENT_CALL_TRACER = "client_call_tracer"
cdef const char* SERVER_CALL_TRACER_FACTORY = "server_call_tracer_factory"

def gcp_observability_enabled() -> bool:
  return gcp_observability_tracing_enabled() or gcp_observability_metrics_enabled()

def gcp_observability_tracing_enabled() -> bool:
  return os.environ.get('GRPC_GCP_OPEN_CENSUS_TRACING_ENABLED', '0') == 'True'

def gcp_observability_metrics_enabled() -> bool:
  return os.environ.get('GRPC_GCP_OPEN_CENSUS_STATS_ENABLED', '0') == 'True'

cdef void set_client_call_tracer_on_call(_CallState call_state, bytes method):
  sys.stderr.write("CPY: grpc_observability found, calling _create_call_tracer in cygrpc.channel._call\n"); sys.stderr.flush()

  sys.stderr.write(f"grpc.CPY: calling _create_client_call_tracer_capsule\n"); sys.stderr.flush()
  capsule = _observability.create_client_call_tracer_capsule(method)
  #sys.stderr.write(f"grpc.CPY: calling PyCapsule_GetPointer\n"); sys.stderr.flush()
  capsule_ptr = cpython.PyCapsule_GetPointer(capsule, CLIENT_CALL_TRACER)
  printf("grpc.CPY: found capsule with address in void* format: %p\n", capsule_ptr)
  grpc_call_set_call_tracer(call_state.c_call, capsule_ptr)

  sys.stderr.write(f"CPY: Saving capsule to call_state\n"); sys.stderr.flush()
  call_state.call_tracer_capsule = capsule

def set_server_call_tracer_factory() -> None:
  if not gcp_observability_enabled():
    return
  sys.stderr.write("grpc.CPY: grpc_observability found, calling _create_call_tracer in cygrpc.channel._call\n"); sys.stderr.flush()

  sys.stderr.write(f"grpc.CPY: calling _create_server_call_tracer_factory_capsule\n"); sys.stderr.flush()
  capsule = _observability.create_server_call_tracer_factory_capsule()

  #sys.stderr.write(f"grpc.CPY: calling PyCapsule_GetPointer\n"); sys.stderr.flush()
  capsule_ptr = cpython.PyCapsule_GetPointer(capsule, SERVER_CALL_TRACER_FACTORY)
  printf("grpc.CPY: found capsule with address in void* format: %p\n", capsule_ptr)
  grpc_register_server_call_tracer_factory(capsule_ptr)

def set_context_from_server_call_tracer(RequestCallEvent event) -> None:
  if not gcp_observability_enabled():
    return
  sys.stderr.write("CPY: calling get_server_call_tracer...\n"); sys.stderr.flush()
  cdef ServerCallTracer* server_call_tracer
  server_call_tracer = static_cast['ServerCallTracer*'](grpc_call_get_call_tracer(event.call.c_call))
  if gcp_observability_tracing_enabled():
    # TraceId and SpanId is hex string, need to convert to str
    trace_id = _decode(codecs.decode(server_call_tracer.TraceId(), 'hex_codec'))
    span_id = _decode(codecs.decode(server_call_tracer.SpanId(), 'hex_codec'))
    is_sampled = server_call_tracer.IsSampled()
    sys.stderr.write(f"CPY: server side context from core with trace_id: {trace_id} span_id: {span_id} is_sampled: {is_sampled}\n"); sys.stderr.flush()
    _observability.save_span_context(trace_id, span_id, is_sampled)

cdef void _observability_init():
  # RegisterOpenCensusPlugin()
  pass
