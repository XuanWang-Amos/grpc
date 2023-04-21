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
import abc
from typing import Any, Optional, TypeVar, Generic, List

from opencensus.trace import execution_context
from opencensus.trace import span_context as span_context_module
from opencensus.trace import trace_options as trace_options_module

import grpc
from grpc_observability import _cyobservability
from grpc_observability import _open_census

_LOGGER = logging.getLogger(__name__)

PyCapsule = TypeVar('PyCapsule')


class GCPOpenCensusObservability(grpc.GrpcObservability):
    exporter: _open_census.Exporter
    config: _open_census.GcpObservabilityConfig

    def __init__(self):
        # 1. Read config.
        # 2. Creating measures and register views.
        # 3. Create and Saves Tracer and Sampler to ContextVar.
        self.config = _cyobservability.read_gcp_observability_config()
        if not self.config:
            raise ValueError("Invalid configuration")
        sys.stderr.write(f"found config in Observability: {self.config}\n"); sys.stderr.flush()

        if self.config.tracing_enabled:
            self._enable_tracing()
        if self.config.stats_enabled:
            self._enable_stats()

    def init(self, exporter: Optional[_open_census.Exporter]=None) -> None:
        if exporter:
            self.exporter = exporter
        else:
            self.exporter = _open_census.OpenCensusExporter(self.config)

        # 4. Start exporting thread.
        try:
            _cyobservability.cyobservability_init(self.exporter)
        except Exception as e:
            _LOGGER.exception("grpc_observability init failed with: {}".format(e))

        # 5. Init grpc.
        grpc.observability_init(self)

    def exit(self) -> None:
        _cyobservability.at_observability_exit()

    def __enter__(self) -> None:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        sys.stderr.write("\nPY: Calling Observability.__exit__\n")
        sys.stderr.flush()
        _cyobservability.at_observability_exit()

    def create_client_call_tracer_capsule(self, method: bytes) -> PyCapsule:
        current_span = execution_context.get_current_span()
        if current_span:
            # Propagate existing OC context
            trace_id = current_span.context_tracer.trace_id.encode('utf8')
            parent_span_id = current_span.span_id.encode('utf8')
            sys.stderr.write(
                f"PY: found trace_id: {trace_id} parent_span_id: {parent_span_id}\n"
            )
            sys.stderr.flush()
            capsule = _cyobservability.create_client_call_tracer_capsule(
                method, trace_id, parent_span_id)
        else:
            trace_id = span_context_module.generate_trace_id().encode('utf8')
            capsule = _cyobservability.create_client_call_tracer_capsule(
                method, trace_id)
        return capsule

    def create_server_call_tracer_factory(self) -> PyCapsule:
        capsule = _cyobservability.create_server_call_tracer_factory_capsule()
        return capsule

    def delete_client_call_tracer(self, client_call_tracer_capsule: PyCapsule) -> None:
        _cyobservability.delete_client_call_tracer(client_call_tracer_capsule)

    def save_trace_context(self, trace_id: str, span_id: str, is_sampled: bool) -> None:
        trace_options = trace_options_module.TraceOptions(0)
        trace_options.set_enabled(is_sampled)
        span_context = span_context_module.SpanContext(trace_id=trace_id,
                                                    span_id=span_id,
                                                    trace_options=trace_options)
        current_tracer = execution_context.get_opencensus_tracer()
        current_tracer.span_context = span_context

    def record_rpc_latency(self, method: str, rpc_latency: float, status_code: Any) -> None:
        status_code = GRPC_STATUS_CODE_TO_STRING.get(status_code, "UNKNOWN")
        sys.stderr.write(f"PY: found double_measure: {method}, {rpc_latency}, {status_code}\n"); sys.stderr.flush()
        _cyobservability._record_rpc_latency(self.exporter, method, rpc_latency, status_code)


GRPC_STATUS_CODE_TO_STRING = {
    grpc.StatusCode.OK: "OK",
    grpc.StatusCode.CANCELLED: "CANCELLED",
    grpc.StatusCode.UNKNOWN: "UNKNOWN",
    grpc.StatusCode.INVALID_ARGUMENT: "INVALID_ARGUMENT",
    grpc.StatusCode.DEADLINE_EXCEEDED: "DEADLINE_EXCEEDED",
    grpc.StatusCode.NOT_FOUND: "NOT_FOUND",
    grpc.StatusCode.ALREADY_EXISTS: "ALREADY_EXISTS",
    grpc.StatusCode.PERMISSION_DENIED: "PERMISSION_DENIED",
    grpc.StatusCode.UNAUTHENTICATED: "UNAUTHENTICATED",
    grpc.StatusCode.RESOURCE_EXHAUSTED: "RESOURCE_EXHAUSTED",
    grpc.StatusCode.FAILED_PRECONDITION: "FAILED_PRECONDITION",
    grpc.StatusCode.ABORTED: "ABORTED",
    grpc.StatusCode.OUT_OF_RANGE: "OUT_OF_RANGE",
    grpc.StatusCode.UNIMPLEMENTED: "UNIMPLEMENTED",
    grpc.StatusCode.INTERNAL: "INTERNAL",
    grpc.StatusCode.UNAVAILABLE: "UNAVAILABLE",
    grpc.StatusCode.DATA_LOSS: "DATA_LOSS",
}
