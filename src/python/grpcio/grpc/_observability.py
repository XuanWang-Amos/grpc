# Copyright 2020 The gRPC authors.
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

import types
import logging
import threading
import abc
import sys
from typing import Any, Optional, TypeVar, Generic

import grpc
from grpc._cython import cygrpc as _cygrpc

_LOGGER = logging.getLogger(__name__)

_TRACING_ENABLED = False
_STATS_ENABLED = False
_O11Y_LOCK = threading.Lock()

PyCapsule = TypeVar('PyCapsule')

class GrpcObservability(Generic[PyCapsule], metaclass=abc.ABCMeta):
    # we need to add hooks so that the GCP observability package can register functions with
    # the grpcio module and so can any other observability module conforming to the interface.

    @abc.abstractmethod
    def create_client_call_tracer_capsule(self, method: bytes) -> PyCapsule:
        raise NotImplementedError()

    @abc.abstractmethod
    def delete_client_call_tracer(self, client_call_tracer_capsule: PyCapsule) -> None:
        # delte client call tracer have to be called on o11y package side.
        # Call it for both segregated and integrated call (`_process_integrated_call_tag`)
        raise NotImplementedError()

    @abc.abstractmethod
    def save_span_context(self, trace_id: str, span_id: str, is_sampled: bool) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def create_server_call_tracer_factory(self) -> PyCapsule:
        raise NotImplementedError()

    @abc.abstractmethod
    def record_rpc_latency(self, method: str, rpc_latency: float, status_code: Any) -> None:
        raise NotImplementedError()

    def _enable_tracing(self) -> None:
        global _TRACING_ENABLED
        with _O11Y_LOCK:
            _TRACING_ENABLED = True

    def _enable_stats(self) -> None:
        global _STATS_ENABLED
        with _O11Y_LOCK:
            _STATS_ENABLED = True

    def _tracing_enabled(self) -> bool:
        with _O11Y_LOCK:
            return _TRACING_ENABLED

    def _stats_enabled(self) -> bool:
        with _O11Y_LOCK:
            return _STATS_ENABLED

    def _observability_enabled(self) -> bool:
        return self._tracing_enabled() or self._stats_enabled()


def observability_init(grpc_observability: GrpcObservability) -> None:
    setattr(grpc, "_grpc_observability", grpc_observability)
    sys.stderr.write(f"ERROR: setattr(grpc): {type(getattr(grpc, '_grpc_observability', None))}\n"); sys.stderr.flush()
    try:
        _cygrpc.set_server_call_tracer_factory()
    except Exception as e:  # pylint:disable=broad-except
        _LOGGER.exception(f"Observability initiazation failed with {e}")
