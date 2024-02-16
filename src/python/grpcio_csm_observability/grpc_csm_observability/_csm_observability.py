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
from typing import Any, Iterable, List, Optional

import grpc

# pytype: disable=pyi-error
from grpc_observability._open_telemetry_exporter import (
    _OpenTelemetryExporterDelegator,
)
from grpc_observability._open_telemetry_plugin import OpenTelemetryPlugin
from grpc_observability._open_telemetry_plugin import _OpenTelemetryPlugin
from grpc_observability import OpenTelemetryObservability

_LOGGER = logging.getLogger(__name__)

ClientCallTracerCapsule = Any  # it appears only once in the function signature
ServerCallTracerFactoryCapsule = (
    Any  # it appears only once in the function signature
)
grpc_observability = Any  # grpc_observability.py imports this module.


_observability_lock: threading.RLock = threading.RLock()
_OPEN_TELEMETRY_OBSERVABILITY: Optional["OpenTelemetryObservability"] = None


# def start_open_telemetry_observability(
#     *,
#     plugins: Optional[Iterable[OpenTelemetryPlugin]] = None,
# ) -> None:
#     global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
#     with _observability_lock:
#         if _OPEN_TELEMETRY_OBSERVABILITY is None:
#             _OPEN_TELEMETRY_OBSERVABILITY = OpenTelemetryObservability(
#                 plugins=plugins
#             )
#             _OPEN_TELEMETRY_OBSERVABILITY.observability_init()
#         else:
#             raise RuntimeError(
#                 "gPRC Python observability was already initiated!"
#             )


# def end_open_telemetry_observability() -> None:
#     global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
#     with _observability_lock:
#         if not _OPEN_TELEMETRY_OBSERVABILITY:
#             raise RuntimeError(
#                 "end_open_telemetry_observability() was called without initiate observability!"
#             )
#         else:
#             _OPEN_TELEMETRY_OBSERVABILITY.observability_deinit()
#             _OPEN_TELEMETRY_OBSERVABILITY = None


# pylint: disable=no-self-use
class CSMOpenTelemetryObservability(OpenTelemetryObservability):
    """OpenTelemetry based plugin implementation.

    This is class is part of an EXPERIMENTAL API.

    Args:
      plugin: OpenTelemetryPlugin to enable.
    """

    exporter: "grpc_observability.Exporter"

    def __init__(
        self,
        *,
        plugins: Optional[Iterable[OpenTelemetryPlugin]] = None,
    ):
        _plugins = self.get_internal_plugins(plugins)
        self.exporter = _OpenTelemetryExporterDelegator(_plugins)

    def __enter__(self):
        global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
        with _observability_lock:
            if _OPEN_TELEMETRY_OBSERVABILITY:
                raise RuntimeError(
                    "gPRC Python observability was already initiated!"
                )
            self.observability_init()
            _OPEN_TELEMETRY_OBSERVABILITY = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
        with _observability_lock:
            self.observability_deinit()
            _OPEN_TELEMETRY_OBSERVABILITY = None

    def get_internal_plugins(plugins: Optional[Iterable[OpenTelemetryPlugin]] = None,
                             ) -> List[_OpenTelemetryPlugin]:
        _plugins = []
        if plugins:
            for plugin in plugins:
                _plugins.append(_OpenTelemetryPlugin(plugin))

        return _plugins
