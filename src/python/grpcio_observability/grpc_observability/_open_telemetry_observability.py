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

import logging
import threading
import time
from typing import Any, AnyStr, Dict, Iterable, List, Optional

import grpc

# pytype: disable=pyi-error
from grpc_observability import _cyobservability
# from grpc_observability._observability import OptionalLabelType

from grpc_observability._open_telemetry_exporter import (
    _OpenTelemetryExporterDelegator,
)
from grpc_observability._open_telemetry_plugin import OpenTelemetryPlugin
from grpc_observability._open_telemetry_plugin import _OpenTelemetryPlugin
from grpc_observability._cyobservability import (
    PLUGIN_IDENTIFIER_SEP,
)

_LOGGER = logging.getLogger(__name__)

ClientCallTracerCapsule = Any  # it appears only once in the function signature
ServerCallTracerFactoryCapsule = Any  # it appears only once in the function signature
grpc_observability = Any  # grpc_observability.py imports this module.

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

_observability_lock: threading.RLock = threading.RLock()
_OPEN_TELEMETRY_OBSERVABILITY: Optional["OpenTelemetryObservability"] = None


def start_open_telemetry_observability(
    *,
    plugins: Optional[Iterable[OpenTelemetryPlugin]] = None,
) -> None:
    global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
    with _observability_lock:
        if _OPEN_TELEMETRY_OBSERVABILITY is None:
            _OPEN_TELEMETRY_OBSERVABILITY = OpenTelemetryObservability(plugins=plugins)
            _OPEN_TELEMETRY_OBSERVABILITY.observability_init()
        else:
            raise RuntimeError("gPRC Python observability was already initiated!")


def end_open_telemetry_observability() -> None:
    global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
    with _observability_lock:
        if not _OPEN_TELEMETRY_OBSERVABILITY:
            raise RuntimeError(
                "end_open_telemetry_observability() was called without initiate observability!"
            )
        else:
            _OPEN_TELEMETRY_OBSERVABILITY.observability_deinit()
            _OPEN_TELEMETRY_OBSERVABILITY = None


# pylint: disable=no-self-use
class OpenTelemetryObservability(grpc._observability.ObservabilityPlugin):
    """OpenTelemetry based plugin implementation.

    This is class is part of an EXPERIMENTAL API.

    Args:
      plugin: OpenTelemetryPlugin to enable.
    """

    _exporter: "grpc_observability.Exporter"
    _plugins: List[_OpenTelemetryPlugin]

    def __init__(
        self,
        *,
        plugins: Optional[Iterable[OpenTelemetryPlugin]] = None,
    ):
        self._plugins = []
        if plugins:
            for plugin in plugins:
                self._plugins.append(_OpenTelemetryPlugin(plugin))

        self._exporter = _OpenTelemetryExporterDelegator(self._plugins)

    def __enter__(self):
        global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
        with _observability_lock:
            if _OPEN_TELEMETRY_OBSERVABILITY:
                raise RuntimeError("gPRC Python observability was already initiated!")
            self.observability_init()
            _OPEN_TELEMETRY_OBSERVABILITY = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
        with _observability_lock:
            self.observability_deinit()
            _OPEN_TELEMETRY_OBSERVABILITY = None

    def observability_init(self):
        try:
            _cyobservability.activate_stats()
            self.set_stats(True)
        except Exception as e:  # pylint: disable=broad-except
            raise ValueError(f"Activate observability metrics failed with: {e}")

        try:
            _cyobservability.cyobservability_init(self._exporter)
        # TODO(xuanwn): Use specific exceptons
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.exception("Initiate observability failed with: %s", e)

        grpc._observability.observability_init(self)

    def observability_deinit(self) -> None:
        # Sleep so we don't loss any data. If we shutdown export thread
        # immediately after exit, it's possible that core didn't call RecordEnd
        # in callTracer, and all data recorded by calling RecordEnd will be
        # lost.
        # CENSUS_EXPORT_BATCH_INTERVAL_SECS: The time equals to the time in
        # AwaitNextBatchLocked.
        # TODO(xuanwn): explicit synchronization
        # https://github.com/grpc/grpc/issues/33262
        time.sleep(_cyobservability.CENSUS_EXPORT_BATCH_INTERVAL_SECS)
        self.set_tracing(False)
        self.set_stats(False)
        _cyobservability.observability_deinit()
        grpc._observability.observability_deinit()

    def create_client_call_tracer(
        self, method_name: bytes, target: bytes
    ) -> ClientCallTracerCapsule:
        trace_id = b"TRACE_ID"
        additional_labels = self._get_additional_client_labels(target)
        enabled_optional_labels = set()
        for plugin in self._plugins:
            enabled_optional_labels.update(plugin.get_enabled_optional_labels())

        capsule = _cyobservability.create_client_call_tracer(
            method_name,
            target,
            trace_id,
            self._get_identifier(),
            additional_labels,
            enabled_optional_labels,
        )
        return capsule

    def create_server_call_tracer_factory(
        self,
        *,
        xds: bool,
    ) -> Optional[ServerCallTracerFactoryCapsule]:
        capsule = None
        additional_labels = self._get_additional_server_labels(xds)
        print(f"server identifier: {self._get_identifier()}")
        if self.is_server_traced(xds):
            capsule = _cyobservability.create_server_call_tracer_factory_capsule(
                additional_labels, self._get_identifier()
            )
        return capsule

    def delete_client_call_tracer(
        self, client_call_tracer: ClientCallTracerCapsule
    ) -> None:
        _cyobservability.delete_client_call_tracer(client_call_tracer)

    def save_trace_context(self, trace_id: str, span_id: str, is_sampled: bool) -> None:
        pass

    def record_rpc_latency(
        self,
        method: str,
        target: str,
        rpc_latency: float,
        status_code: grpc.StatusCode,
    ) -> None:
        status_code = GRPC_STATUS_CODE_TO_STRING.get(status_code, "UNKNOWN")
        _cyobservability._record_rpc_latency(
            self._exporter,
            method,
            target,
            rpc_latency,
            status_code,
            self._get_identifier(),
        )

    def _get_additional_client_labels(self, target: bytes) -> Dict[str, AnyStr]:
        additional_client_labels = {}
        for _plugin in self._plugins:
            additional_client_labels.update(
                _plugin.get_additional_client_labels(target)
            )
        print(f"additional_client_labels: {additional_client_labels}")
        return additional_client_labels

    def _get_additional_server_labels(self, xds: bool) -> Dict[str, str]:
        additional_server_labels = {}
        for _plugin in self._plugins:
            additional_server_labels.update(_plugin.get_additional_server_labels(xds))
        print(f"additional_server_labels: {additional_server_labels}")
        return additional_server_labels

    def _get_identifier(self) -> str:
        plugin_identifiers = []
        for _plugin in self._plugins:
            plugin_identifiers.append(_plugin.identifier)
        return PLUGIN_IDENTIFIER_SEP.join(plugin_identifiers)

    def is_server_traced(self, xds: bool) -> bool:
        return True
