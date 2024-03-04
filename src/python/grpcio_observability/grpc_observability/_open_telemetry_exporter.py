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

from typing import Dict, List

from grpc_observability import _observability  # pytype: disable=pyi-error
from grpc_observability._open_telemetry_plugin import _OpenTelemetryPlugin


class _OpenTelemetryExporterDelegator(_observability.Exporter):
    _plugin_map: Dict[str, _OpenTelemetryPlugin]

    def __init__(self, plugins: List[_OpenTelemetryPlugin]):
        self._plugin_map = {}
        for plugin in plugins:
            self._plugin_map[plugin.identifier] = plugin

    def export_stats_data(
        self, stats_data: List[_observability.StatsData]
    ) -> None:
        for data in stats_data:
            for identifier in data.identifiers:
                if identifier in self._plugin_map.keys():
                    self._plugin_map[identifier].maybe_record_stats_data(data)

    def export_tracing_data(
        self, tracing_data: List[_observability.TracingData]
    ) -> None:
        pass
