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

from typing import Optional

import sys
import time
import grpc
import logging

from opencensus.trace import execution_context, samplers
from opencensus.trace.tracer import Tracer
from opencensus.trace.tracers import context_tracer, noop_tracer
from opencensus.trace import span_context as span_context_module
from opencensus.trace import trace_options as trace_options_module

from grpc_observability import _cyobservability
from grpc_observability import _open_census

_LOGGER = logging.getLogger(__name__)


class Observability:

    def __init__(self):
        sys.stderr.write("\nPY: Calling Observability.__init__\n")
        sys.stderr.flush()

    def __enter__(self):
        sys.stderr.write("\nPY: Calling Observability.__enter__\n")
        sys.stderr.flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.write("\nPY: Calling Observability.__exit__\n")
        sys.stderr.flush()
        _cyobservability.at_observability_exit()
        return False

    def __del__(self):
        pass

    def init(self):
        sys.stderr.write(f"\nPY: Calling Observability.init\n")
        sys.stderr.flush()

        # 1. Read config
        # 2. Creating measures and register views
        # 3. Create and Saves Tracer and Sampler to ContextVar
        # TODO(xuanwn): Errors out if config is invalid.
        _cyobservability.observability_init()

        config = _open_census.gcpObservabilityConfig.get()
        sys.stderr.write(f"------->>> Found Config:\n{config}\n")
        sys.stderr.flush()

        # 4. Inject server call tracer factory
        grpc.observability_init()


def _create_client_call_tracer_capsule(**kwargs) -> object:
    method = kwargs['method']
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
    sys.stderr.write(f"PY: created client tracer capsule: {capsule}\n")
    sys.stderr.flush()
    return capsule


def _create_server_call_tracer_factory_capsule(**kwargs) -> object:
    capsule = _cyobservability.create_server_call_tracer_factory_capsule()
    sys.stderr.write(f"PY: created server factory capsule: {capsule}\n")
    sys.stderr.flush()
    return capsule


def _save_span_context(**kwargs) -> None:
    trace_options = trace_options_module.TraceOptions(0)
    trace_options.set_enabled(kwargs['is_sampled'])
    span_context = span_context_module.SpanContext(trace_id=kwargs['trace_id'],
                                                   span_id=kwargs['span_id'],
                                                   trace_options=trace_options)
    current_tracer = execution_context.get_opencensus_tracer()
    current_tracer.span_context = span_context
