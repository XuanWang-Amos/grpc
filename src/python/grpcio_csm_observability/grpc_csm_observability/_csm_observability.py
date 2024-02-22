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
from grpc_observability._open_telemetry_plugin import _OpenTelemetryPlugin
from grpc_observability._observability import OptionalLabelType
from grpc_observability import OpenTelemetryObservability
from grpc_csm_observability._csm_observability_plugin import (
    CSMOpenTelemetryPlugin,
    _CSMOpenTelemetryPlugin,
)
from grpc_observability._open_telemetry_observability import (
    _OPEN_TELEMETRY_OBSERVABILITY,
    _observability_lock,
)

_LOGGER = logging.getLogger(__name__)


def start_csm_observability(
    *,
    plugins: Optional[Iterable[CSMOpenTelemetryPlugin]] = None,
) -> None:
    global _OPEN_TELEMETRY_OBSERVABILITY  # pylint: disable=global-statement
    with _observability_lock:
        if _OPEN_TELEMETRY_OBSERVABILITY is None:
            _OPEN_TELEMETRY_OBSERVABILITY = CSMOpenTelemetryObservability(
                plugins=plugins
            )
            _OPEN_TELEMETRY_OBSERVABILITY.observability_init()
        else:
            raise RuntimeError("gPRC Python observability was already initiated!")


def end_csm_observability() -> None:
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
class CSMOpenTelemetryObservability(OpenTelemetryObservability):
    """OpenTelemetry based plugin implementation.

    This is class is part of an EXPERIMENTAL API.

    Args:
      plugin: CSMOpenTelemetryPlugin to enable.
      csm_diagnostic_reporting_enabled: Whether send csm diagnostic reports to TD.
    """

    _exporter: "grpc_observability.Exporter"

    def __init__(
        self,
        *,
        plugins: Optional[Iterable[CSMOpenTelemetryPlugin]] = None,
        csm_diagnostic_reporting_enabled: Optional[bool] = True,
    ):
        self._plugins = []
        if plugins:
            for plugin in plugins:
                self._plugins.append(_OpenTelemetryPlugin(plugin))

        if csm_diagnostic_reporting_enabled:
            _csm_plugin = self._build_csm_plugin()
            self._plugins.append(_csm_plugin)

        self._exporter = _OpenTelemetryExporterDelegator(self._plugins)

    def _build_csm_plugin(self) -> _OpenTelemetryPlugin:
        return _OpenTelemetryPlugin(_CSMOpenTelemetryPlugin())

    def get_enabled_optional_labels(self) -> List[OptionalLabelType]:
        return [OptionalLabelType.XDS_SERVICE_LABELS]
