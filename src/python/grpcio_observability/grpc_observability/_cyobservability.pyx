# Copyright 2023 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cimport cpython
from cython.operator cimport dereference

import sys
import os
import logging
from threading import Thread
from typing import List, Tuple, Mapping, TypeVar, Optional

from grpc_observability import _open_census
from grpc_observability import _measures

cdef const char* CLIENT_CALL_TRACER = "gcp_opencensus_client_call_tracer"
cdef const char* SERVER_CALL_TRACER_FACTORY = "gcp_opencensus_server_call_tracer_factory"
cdef bint GLOBAL_SHUTDOWN_EXPORT_THREAD = False
cdef object global_export_thread

_LOGGER = logging.getLogger(__name__)
PyCapsule = TypeVar('PyCapsule')

class PyMetric:
  def __init__(self, measurement, labels):
    self.name = measurement['name']
    self.labels = labels
    self.measure = METRICS_NAME_TO_MEASURE.get(self.name)
    if measurement['type'] == kMeasurementDouble:
      self.measure_double = True
      self.measure_value = measurement['value']['value_double']
    else:
      self.measure_double = False
      self.measure_value = measurement['value']['value_int']

class PySpan:
  def __init__(self, span_data, span_labels, span_annotations):
      self.name = _decode(span_data['name'])
      self.start_time = _decode(span_data['start_time'])
      self.end_time = _decode(span_data['end_time'])
      self.trace_id = _decode(span_data['trace_id'])
      self.span_id = _decode(span_data['span_id'])
      self.parent_span_id = _decode(span_data['parent_span_id'])
      self.status = _decode(span_data['status'])
      self.span_labels = span_labels
      self.span_annotations = span_annotations
      self.should_sample = span_data['should_sample']
      self.child_span_count = span_data['child_span_count']


class MetricsName:
  CLIENT_API_LATENCY = kRpcClientApiLatencyMeasureName
  CLIENT_SNET_MESSSAGES_PER_RPC = kRpcClientSentMessagesPerRpcMeasureName
  CLIENT_SEND_BYTES_PER_RPC = kRpcClientSentBytesPerRpcMeasureName
  CLIENT_RECEIVED_MESSAGES_PER_RPC = kRpcClientReceivedMessagesPerRpcMeasureName
  CLIENT_RECEIVED_BYTES_PER_RPC = kRpcClientReceivedBytesPerRpcMeasureName
  CLIENT_ROUNDTRIP_LATENCY = kRpcClientRoundtripLatencyMeasureName
  CLIENT_SERVER_LATENCY = kRpcClientServerLatencyMeasureName
  CLIENT_STARTED_RPCS = kRpcClientStartedRpcsMeasureName
  CLIENT_RETRIES_PER_CALL = kRpcClientRetriesPerCallMeasureName
  CLIENT_TRANSPARENT_RETRIES_PER_CALL = kRpcClientTransparentRetriesPerCallMeasureName
  CLIENT_RETRY_DELAY_PER_CALL = kRpcClientRetryDelayPerCallMeasureName
  CLIENT_TRANSPORT_LATENCY = kRpcClientTransportLatencyMeasureName
  SERVER_SENT_MESSAGES_PER_RPC = kRpcServerSentMessagesPerRpcMeasureName
  SERVER_SENT_BYTES_PER_RPC = kRpcServerSentBytesPerRpcMeasureName
  SERVER_RECEIVED_MESSAGES_PER_RPC = kRpcServerReceivedMessagesPerRpcMeasureName
  SERVER_RECEIVED_BYTES_PER_RPC = kRpcServerReceivedBytesPerRpcMeasureName
  SERVER_SERVER_LATENCY = kRpcServerServerLatencyMeasureName
  SERVER_STARTED_RPCS = kRpcServerStartedRpcsMeasureName

METRICS_NAME_TO_MEASURE = {
  MetricsName.CLIENT_API_LATENCY: _measures.rpc_client_api_latency(),
  MetricsName.CLIENT_SNET_MESSSAGES_PER_RPC: _measures.rpc_client_sent_messages_per_rpc(),
  MetricsName.CLIENT_SEND_BYTES_PER_RPC: _measures.rpc_client_send_bytes_per_prc(),
  MetricsName.CLIENT_RECEIVED_MESSAGES_PER_RPC: _measures.rpc_client_received_messages_per_rpc(),
  MetricsName.CLIENT_RECEIVED_BYTES_PER_RPC: _measures.rpc_client_received_bytes_per_rpc(),
  MetricsName.CLIENT_ROUNDTRIP_LATENCY: _measures.rpc_client_roundtrip_latency(),
  MetricsName.CLIENT_SERVER_LATENCY: _measures.rpc_client_server_latency(),
  MetricsName.CLIENT_STARTED_RPCS: _measures.rpc_client_started_rpcs(),
  MetricsName.CLIENT_RETRIES_PER_CALL: _measures.rpc_client_retries_per_call(),
  MetricsName.CLIENT_TRANSPARENT_RETRIES_PER_CALL: _measures.rpc_client_transparent_retries_per_call(),
  MetricsName.CLIENT_RETRY_DELAY_PER_CALL: _measures.rpc_client_retry_delay_per_call(),
  MetricsName.CLIENT_TRANSPORT_LATENCY: _measures.rpc_client_transport_latency(),
  MetricsName.SERVER_SENT_MESSAGES_PER_RPC: _measures.rpc_server_sent_messages_per_rpc(),
  MetricsName.SERVER_SENT_BYTES_PER_RPC: _measures.rpc_server_sent_bytes_per_rpc(),
  MetricsName.SERVER_RECEIVED_MESSAGES_PER_RPC: _measures.rpc_server_received_messages_per_rpc(),
  MetricsName.SERVER_RECEIVED_BYTES_PER_RPC: _measures.rpc_server_received_bytes_per_rpc(),
  MetricsName.SERVER_SERVER_LATENCY: _measures.rpc_server_server_latency(),
  MetricsName.SERVER_STARTED_RPCS: _measures.rpc_server_started_rpcs(),
}

def cyobservability_init() -> None:
  gcpObservabilityInit() # remove print buffer
  _start_exporting_thread()


def _start_exporting_thread() -> None:
  global global_export_thread
  global_export_thread = Thread(target=_export_census_data)
  printf("> Exporting Thread: ------------ STARTING Exporting Thread ------------\n")
  global_export_thread.start()


def read_gcp_observability_config() -> Optional[_open_census.GcpObservabilityConfig]:
  py_labels = {}
  sampling_rate = 0.0
  tracing_enabled = False
  stats_enabled = False

  cdef cGcpObservabilityConfig c_config = ReadObservabilityConfig()
  if not c_config.is_valid:
    return None

  for label in c_config.labels:
    py_labels[_decode(label.key)] = _decode(label.value)

  if PythonOpenCensusTracingEnabled():
    sampling_rate = c_config.cloud_trace.sampling_rate
    tracing_enabled = True
    # Save sampling rate to global sampler.
    ProbabilitySampler.Get().SetThreshold(sampling_rate)

  if PythonOpenCensusStatsEnabled():
    stats_enabled = True

  py_config = _open_census.GcpObservabilityConfig.get()
  py_config.set_configuration(_decode(c_config.project_id), sampling_rate,
                              py_labels, tracing_enabled, stats_enabled)
  sys.stderr.write(f"After set_configuration: {py_config}\n"); sys.stderr.flush()
  return py_config


def create_client_call_tracer_capsule(bytes method, bytes trace_id,
                                      bytes parent_span_id=b'') -> cpython.PyObject:
  cdef char* c_method = cpython.PyBytes_AsString(method)
  cdef char* c_trace_id = cpython.PyBytes_AsString(trace_id)
  cdef char* c_parent_span_id = cpython.PyBytes_AsString(parent_span_id)

  cdef void* call_tracer = CreateClientCallTracer(c_method, c_trace_id, c_parent_span_id)
  capsule = cpython.PyCapsule_New(call_tracer, CLIENT_CALL_TRACER, NULL)
  return capsule


def create_server_call_tracer_factory_capsule() -> cpython.PyObject:
  cdef void* call_tracer_factory = CreateServerCallTracerFactory()

  capsule = cpython.PyCapsule_New(call_tracer_factory, SERVER_CALL_TRACER_FACTORY, NULL)
  return capsule


def delete_client_call_tracer(client_call_tracer_capsule: PyCapsule) -> None:
  sys.stderr.write(f"~~~~~~~~~~~~~~ CPY: calling delete_client_call_tracer\n"); sys.stderr.flush()
  if cpython.PyCapsule_IsValid(client_call_tracer_capsule, "gcp_opencensus_client_call_tracer"):
    capsule_ptr = cpython.PyCapsule_GetPointer(client_call_tracer_capsule, "gcp_opencensus_client_call_tracer")
    #sys.stderr.write(f"~~~~~~~~~~~~~~ capsule_ptr: {capsule_ptr}\n"); sys.stderr.flush()
    call_tracer_ptr = <ClientCallTracer*>capsule_ptr
    #printf("~~~~~~~~~~~~~~ <CallTracer*>capsule_ptr: %p\n", call_tracer_ptr)
    sys.stderr.write(f"~~~~~~~~~~~~~~ CPY: deling call_tracer_ptr\n"); sys.stderr.flush()
    del call_tracer_ptr

def _c_label_to_labels(cLabels) -> Mapping[str, str]:
  py_labels = {}
  for label in cLabels:
    py_labels[_decode(label['key'])] = _decode(label['value'])
  return py_labels


def _c_annotation_to_annotations(cAnnotations) -> List[Tuple[str, str]]:
  py_annotations = []
  for annotation in cAnnotations:
    py_annotations.append((_decode(annotation['time_stamp']),
                          _decode(annotation['description'])))
  return py_annotations


def at_observability_exit() -> None:
  _shutdown_exporting_thread()


def _record_rpc_latency(str method, float rpc_latency, status_code) -> None:
  measurement = {}
  measurement['name'] = kRpcClientApiLatencyMeasureName
  measurement['type'] = kMeasurementDouble
  measurement['value'] = {'value_double': rpc_latency}

  labels = {}
  labels[_decode(kClientMethod)] = method.strip("/")
  labels[_decode(kClientStatus)] = status_code
  metric = PyMetric(measurement, labels)
  _open_census.export_metric_batch([metric])


cdef void _export_census_data():
  while True:
    with nogil:
      while not GLOBAL_SHUTDOWN_EXPORT_THREAD:
        lk = new unique_lock[mutex](kCensusDataBufferMutex)
        # Wait for next batch of census data OR timeout at fixed interval.
        # Batch export census data to minimize the time we acquiring the GIL.
        AwaitNextBatchLocked(dereference(lk), 500)

        # Break only when buffer have data
        if not kCensusDataBuffer.empty():
          del lk
          break
        else:
          del lk

    _flush_census_data()

    if GLOBAL_SHUTDOWN_EXPORT_THREAD:
      break # Break to shutdown exporting thead
  sys.stderr.write(f"> Exporting Thread: _export_census_data shutting down...\n"); sys.stderr.flush()


cdef void _flush_census_data():
  lk = new unique_lock[mutex](kCensusDataBufferMutex)
  with nogil:
    if kCensusDataBuffer.empty():
      del lk
      return
  printf("> Exporting Thread: >>>>>>>> queue NOT empty, flushing data...\n")
  py_metrics_batch = []
  py_spans_batch = []
  while not kCensusDataBuffer.empty():
    cCensusData = kCensusDataBuffer.front()
    if cCensusData.type == kMetricData:
      py_labels = _c_label_to_labels(cCensusData.labels)
      py_metric = PyMetric(cCensusData.measurement_data, py_labels)
      py_metrics_batch.append(py_metric)
    else:
      py_span_labels = _c_label_to_labels(cCensusData.span_data.span_labels)
      py_span_annotations = _c_annotation_to_annotations(cCensusData.span_data.span_annotations)
      py_span = PySpan(cCensusData.span_data, py_span_labels, py_span_annotations)
      py_spans_batch.append(py_span)
    kCensusDataBuffer.pop()

  _open_census.export_metric_batch(py_metrics_batch)
  _open_census.export_span_batch(py_spans_batch)
  del lk

cdef void _shutdown_exporting_thread():
  with nogil:
    global GLOBAL_SHUTDOWN_EXPORT_THREAD
    printf("------------ shutting down exporting thread\n")
    GLOBAL_SHUTDOWN_EXPORT_THREAD = True
    CensusDataBufferCV.notify_all()
  printf("------------ waiting export thead to end...\n")
  global_export_thread.join()


cdef str _decode(bytes bytestring):
    if isinstance(bytestring, (str,)):
        return <str>bytestring
    else:
        try:
            return bytestring.decode('utf8')
        except UnicodeDecodeError:
            _LOGGER.exception('Invalid encoding on %s', bytestring)
            return bytestring.decode('latin1')
