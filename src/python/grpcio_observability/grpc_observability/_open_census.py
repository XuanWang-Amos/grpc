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

import sys
import logging
import views
import collections
from typing import AnyStr, Optional, List, Tuple, Mapping
from datetime import datetime

from google.rpc import code_pb2

from opencensus.stats import stats as stats_module
from opencensus.tags.tag_key import TagKey
from opencensus.tags.tag_value import TagValue
from opencensus.tags.tag_map import TagMap
from opencensus.trace.span import SpanKind
from opencensus.trace.status import Status
from opencensus.trace.tracer import Tracer
from opencensus.trace import span_context as span_context_module
from opencensus.trace import execution_context, samplers
from opencensus.trace import span_data as span_data_module
from opencensus.trace import time_event
from opencensus.trace import trace_options as trace_options_module

logger = logging.getLogger(__name__)

_Label = collections.namedtuple('_Label', (
    'key',
    'tag_key',
    'value',
))

VIEW_NAMES = [
    "grpc.io/client/started_rpcs",
    #   "grpc.io/client/completed_rpcs",
    #   "grpc.io/client/roundtrip_latency",
    #   "grpc.io/client/sent_compressed_message_bytes_per_rpc",
    #   "grpc.io/client/received_compressed_message_bytes_per_rpc",
    #   "grpc.io/server/started_rpcs",
    #   "grpc.io/server/completed_rpcs",
    #   "grpc.io/server/sent_compressed_message_bytes_per_rpc",
    #   "grpc.io/server/received_compressed_message_bytes_per_rpc",
    #   "grpc.io/server/server_latency"
]


class gcpObservabilityConfig:
    _singleton = None

    def __init__(self):
        self.project_id = ""
        self.monitoring_enabled = False
        self.tracing_enabled = False
        self.labels = []
        self.sampler = None
        self.sampling_rate = 0.0
        self.tracer = None

    @staticmethod
    def get():
        if gcpObservabilityConfig._singleton is None:
            gcpObservabilityConfig._singleton = gcpObservabilityConfig()
        return gcpObservabilityConfig._singleton

    def set_configuration(self,
                          project_id,
                          sampling_rate=0.0,
                          labels=None,
                          tracing_enabled=False,
                          monitoring_enabled=False):
        self.project_id = project_id
        self.monitoring_enabled = monitoring_enabled
        self.tracing_enabled = tracing_enabled
        self.labels = []
        self.sampling_rate = sampling_rate
        for key, value in labels.items():
            self.labels.append(_Label(key, TagKey(key), value))

        view_manager = stats_module.stats.view_manager
        self.register_open_census_views(view_manager)

    def register_open_census_views(self, view_manager) -> None:
        # Client
        view_manager.register_view(views.client_started_rpcs())
        view_manager.register_view(views.client_completed_rpcs())
        view_manager.register_view(views.client_roundtrip_latency())
        view_manager.register_view(views.client_sent_compressed_message_bytes_per_rpc())
        view_manager.register_view(views.client_received_compressed_message_bytes_per_rpc())

        # Server
        view_manager.register_view(views.server_started_rpcs())
        view_manager.register_view(views.server_completed_rpcs())
        view_manager.register_view(views.server_sent_compressed_message_bytes_per_rpc())
        view_manager.register_view(views.server_received_compressed_message_bytes_per_rpc())
        view_manager.register_view(views.server_server_latency())

    def set_tracer(self) -> None:
        current_tracer = execution_context.get_opencensus_tracer()
        trace_id = current_tracer.span_context.trace_id
        span_id = current_tracer.span_context.span_id
        if not span_id:
            span_id = span_context_module.generate_span_id()
        span_context = span_context_module.SpanContext(trace_id=trace_id,
                                                       span_id=span_id)
        # Create and Saves Tracer and Sampler to ContextVar
        sampler = samplers.ProbabilitySampler(rate=self.sampling_rate)
        # TODO: check existing SpanContext
        self.tracer = Tracer(sampler=sampler, span_context=span_context)

    def __repr__(self):
        labels_str = "\n"
        for label in self.labels:
            labels_str += f"Key:{label.key}, TagKey:{label.tag_key}, Value:{label.value}\n"

        rst = f"gcpObservabilityConfig(project_id={self.project_id},monitoring_enabled={self.monitoring_enabled}"
        rst += f",tracing_enabled={self.tracing_enabled},sampling_rate={self.sampling_rate},labels={labels_str})"
        return rst

    __str__ = __repr__


def export_metric_batch(py_metrics_batch: list) -> None:
    if not py_metrics_batch:
        return
    config = gcpObservabilityConfig.get()
    stats = stats_module.stats
    stats_recorder = stats.stats_recorder
    mmap = stats_recorder.new_measurement_map()

    for metric in py_metrics_batch:
        measure = metric.measure
        if measure is None:
            continue

        tag_map = _get_tag_map(metric.labels, config.labels)

        if metric.measure_double:
            sys.stderr.write(
                f"---->>> PY: measure_float_put with name:{measure.name}, value: {metric.measure_value}, tags: {tag_map.map}\n"
            )
            sys.stderr.flush()
            mmap.measure_float_put(measure, metric.measure_value)
        else:
            sys.stderr.write(
                f"---->>> PY: measure_int_put with name:{measure.name}, value: {metric.measure_value}, tags: {tag_map.map}\n"
            )
            sys.stderr.flush()
            mmap.measure_int_put(measure, metric.measure_value)

        mmap.record(tag_map)


def export_span_batch(py_span_batch: list) -> None:
    if not py_span_batch:
        return

    config = gcpObservabilityConfig.get()
    for span_data in py_span_batch:
        span_context = span_context_module.SpanContext(
            trace_id=span_data.trace_id,
            span_id=span_data.span_id,
            trace_options=trace_options_module.TraceOptions(1))
        span_data = _get_span_datas(span_data, span_context, config.labels)
        sys.stderr.write(f"---->>> PY: span_data: {span_data}\n")
        # self.exporter.export(span_datas)


def _get_tag_map(labels: Mapping[AnyStr, AnyStr],
                 config_labels: Mapping[str, str]) -> TagMap:
    tag_map = TagMap()

    for label in config_labels:
        tag_map.insert(label.tag_key, TagValue(label.value))

    for key, value in labels.items():
        tag_map.insert(TagKey(key), TagValue(value))

    return tag_map


def _get_span_attirbutes(span_labels: Mapping[AnyStr, AnyStr],
                         config_labels: Mapping[str, str]) -> TagMap:
    span_attributes = {}

    for label in config_labels:
        span_attributes[label.key] = label.value

    span_attributes.update(span_labels)

    return span_attributes


def _get_span_annotations(
        span_annotations: List[Tuple[bytes,
                                     bytes]]) -> List[time_event.Annotation]:
    annotations = []

    for time_stamp, description in span_annotations:
        time = datetime.fromisoformat(time_stamp)
        annotations.append(time_event.Annotation(time, description))

    return annotations


def _status_to_span_status(status: str) -> Optional[Status]:
    if status == "OK":
        return Status(code_pb2.OK, message=status)
    elif status == "CANCELLED":
        return Status(code_pb2.CANCELLED, message=status)
    elif status == "UNKNOWN":
        return Status(code_pb2.UNKNOWN, message=status)
    elif status == "INVALID_ARGUMENT":
        return Status(code_pb2.INVALID_ARGUMENT, message=status)
    elif status == "DEADLINE_EXCEEDED":
        return Status(code_pb2.DEADLINE_EXCEEDED, message=status)
    elif status == "NOT_FOUND":
        return Status(code_pb2.NOT_FOUND, message=status)
    elif status == "ALREADY_EXISTS":
        return Status(code_pb2.ALREADY_EXISTS, message=status)
    elif status == "PERMISSION_DENIED":
        return Status(code_pb2.PERMISSION_DENIED, message=status)
    elif status == "UNAUTHENTICATED":
        return Status(code_pb2.UNAUTHENTICATED, message=status)
    elif status == "RESOURCE_EXHAUSTED":
        return Status(code_pb2.RESOURCE_EXHAUSTED, message=status)
    elif status == "FAILED_PRECONDITION":
        return Status(code_pb2.FAILED_PRECONDITION, message=status)
    elif status == "ABORTED":
        return Status(code_pb2.ABORTED, message=status)
    elif status == "OUT_OF_RANGE":
        return Status(code_pb2.OUT_OF_RANGE, message=status)
    elif status == "UNIMPLEMENTED":
        return Status(code_pb2.UNIMPLEMENTED, message=status)
    elif status == "INTERNAL":
        return Status(code_pb2.INTERNAL, message=status)
    elif status == "UNAVAILABLE":
        return Status(code_pb2.UNAVAILABLE, message=status)
    elif status == "DATA_LOSS":
        return Status(code_pb2.DATA_LOSS, message=status)
    else:
        return None


def _get_span_datas(span_data, span_context, labels):
    """Extracts a list of SpanData tuples from a span

    :rtype: list of opencensus.trace.span_data.SpanData
    :return list of SpanData tuples
    """
    span_attributes = _get_span_attirbutes(span_data.span_labels, labels)
    span_status = _status_to_span_status(span_data.status)
    span_annotations = _get_span_annotations(span_data.span_annotations)
    span_datas = [
        span_data_module.SpanData(name=span_data.name,
                                  context=span_context,
                                  span_id=span_data.span_id,
                                  parent_span_id=span_data.parent_span_id
                                  if span_data.parent_span_id else None,
                                  attributes=span_attributes,
                                  start_time=span_data.start_time,
                                  end_time=span_data.end_time,
                                  child_span_count=span_data.child_span_count,
                                  stack_trace=None,
                                  annotations=span_annotations,
                                  message_events=None,
                                  links=None,
                                  status=span_status,
                                  same_process_as_parent_span=True
                                  if span_data.parent_span_id else None,
                                  span_kind=SpanKind.UNSPECIFIED)
    ]

    return span_datas
