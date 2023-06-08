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

from datetime import datetime
from typing import List, Mapping, Optional, Tuple

from google.rpc import code_pb2
from grpc_observability import _observability  # pytype: disable=pyi-error
from grpc_observability import _views
from opencensus.ext.stackdriver import stats_exporter as stackdriver
from opencensus.stats import stats as stats_module
from opencensus.tags.tag_key import TagKey
from opencensus.tags.tag_map import TagMap
from opencensus.tags.tag_value import TagValue
from opencensus.trace import span_context as span_context_module
from opencensus.trace import span_data as span_data_module
from opencensus.trace import time_event
from opencensus.trace import trace_options as trace_options_module
from opencensus.trace.span import SpanKind
from opencensus.trace.status import Status
from opencensus.trace.tracer import Tracer
from opencensus.trace import execution_context
from opencensus.trace import samplers
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter


class OpenCensusExporter(_observability.Exporter):
    default_labels: Optional[Mapping[str, str]]

    def __init__(self, config):
        self.config = config.get()
        self.default_labels = self.config.labels
        self.project_id = self.config.project_id
        self.tracer = None
        self.view_manager = None
        self.measurement_map = None
        self._setup_open_census_stackdriver_exporter()

    def _setup_open_census_stackdriver_exporter(self) -> None:
        if self.config.stats_enabled:
            stats = stats_module.stats
            stats_recorder = stats.stats_recorder
            self.view_manager = stats.view_manager
            options = stackdriver.Options(project_id=self.project_id,
                                          resource="global")
            stats_exporter = stackdriver.new_stats_exporter(options, interval=5)
            self.view_manager.register_exporter(stats_exporter)
            self.measurement_map = stats_recorder.new_measurement_map()
            self._register_open_census_views()


        if self.config.tracing_enabled:
            current_tracer = execution_context.get_opencensus_tracer()
            trace_id = current_tracer.span_context.trace_id
            span_id = current_tracer.span_context.span_id
            if not span_id:
                span_id = span_context_module.generate_span_id()
            span_context = span_context_module.SpanContext(trace_id=trace_id,
                                                        span_id=span_id)
            # Create and Saves Tracer and Sampler to ContextVar
            sampler = samplers.ProbabilitySampler(rate=self.config.sampling_rate)
            self.trace_exporter = StackdriverExporter(project_id=self.project_id)
            self.tracer = Tracer(sampler=sampler,
                                 span_context=span_context,
                                 exporter=self.trace_exporter)

    def export_stats_data(self,
                          stats_data: List[_observability.StatsData]) -> None:
        for metric in stats_data:
            measure = _views.METRICS_NAME_TO_MEASURE.get(metric.name, None)
            if measure is None:
                continue

            labels = metric.labels
            labels.update(self.default_labels)
            tag_map = TagMap()
            for key, value in labels.items():
                tag_map.insert(TagKey(key), TagValue(value))

            if metric.measure_double:
                self.measurement_map.measure_float_put(measure, metric.value_float)
            else:
                self.measurement_map.measure_int_put(measure, metric.value_int)
            self.measurement_map.record(tag_map)


    def export_tracing_data(
            self, tracing_data: List[_observability.TracingData]) -> None:
        for span_data in tracing_data:
            span_context = span_context_module.SpanContext(
                trace_id=span_data.trace_id,
                span_id=span_data.span_id,
                trace_options=trace_options_module.TraceOptions(1))
            span_datas = _get_span_datas(span_data, span_context,
                                        self.default_labels)
            self.trace_exporter.export(span_datas)


    def _register_open_census_views(self) -> None:
        # Client
        self.view_manager.register_view(
            _views.client_started_rpcs(self.default_labels))
        self.view_manager.register_view(
            _views.client_completed_rpcs(self.default_labels))
        self.view_manager.register_view(
            _views.client_roundtrip_latency(self.default_labels))
        self.view_manager.register_view(
            _views.client_api_latency(self.default_labels))
        self.view_manager.register_view(
            _views.client_sent_compressed_message_bytes_per_rpc(
                self.default_labels))
        self.view_manager.register_view(
            _views.client_received_compressed_message_bytes_per_rpc(
                self.default_labels))

        # Server
        self.view_manager.register_view(
            _views.server_started_rpcs(self.default_labels))
        self.view_manager.register_view(
            _views.server_completed_rpcs(self.default_labels))
        self.view_manager.register_view(
            _views.server_sent_compressed_message_bytes_per_rpc(
                self.default_labels))
        self.view_manager.register_view(
            _views.server_received_compressed_message_bytes_per_rpc(
                self.default_labels))
        self.view_manager.register_view(
            _views.server_server_latency(self.default_labels))


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


def _get_span_datas(span_data, span_context, labels: Mapping[str, str]):
    """Extracts a list of SpanData tuples from a span.

    :rtype: list of opencensus.trace.span_data.SpanData
    :return list of SpanData tuples
    """
    span_attributes = span_data.span_labels
    span_attributes.update(labels)
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
