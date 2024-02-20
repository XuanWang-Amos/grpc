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

import abc
from typing import Dict, Iterable, List, Optional, Union

# pytype: disable=pyi-error
import grpc
from grpc_observability import _open_telemetry_measures
from grpc_observability._cyobservability import MetricsName
from grpc_observability._observability import StatsData
from grpc_observability._open_telemetry_plugin import OpenTelemetryPlugin
from grpc_observability._open_telemetry_plugin import _OpenTelemetryPlugin
from grpc_observability._open_telemetry_plugin import OpenTelemetryLabelInjector
from grpc_observability._open_telemetry_plugin import OpenTelemetryPluginOption
from opentelemetry.metrics import Counter
from opentelemetry.metrics import Histogram
from opentelemetry.metrics import Meter
from opentelemetry.metrics import MeterProvider

GRPC_METHOD_LABEL = "grpc.method"
GRPC_TARGET_LABEL = "grpc.target"
GRPC_OTHER_LABEL_VALUE = "other"


class CSMOpenTelemetryLabelInjector(OpenTelemetryLabelInjector):
    """
    An interface that allows you to add additional labels on the calls traced.

    Please note that this class is still work in progress and NOT READY to be used.
    """

    _labels: Dict[str, str]

    def __init__(self):
        # Calls Python OTel API to detect resource and get labels, save
        # those lables to OpenTelemetryLabelInjector.labels.
        self._labels = {"injector_label": "value_for_injector_label"}


    def get_labels(self):
        # Get additional labels for this OpenTelemetryLabelInjector.
        return self._labels


class CSMOpenTelemetryPluginOption(OpenTelemetryPluginOption):
    """
    An interface that allows you to add additional function to OpenTelemetryPlugin.

    Please note that this class is still work in progress and NOT READY to be used.
    """

    def is_active_on_method(self, method: str) -> bool:
        """Determines whether this plugin option is active on a given method.

        Args:
          method: Required. The RPC method, for example: `/helloworld.Greeter/SayHello`.

        Returns:
          True if this this plugin option is active on the giving method, false otherwise.
        """
        return True

    def is_active_on_server(self, xds: bool) -> bool:
        """Determines whether this plugin option is active on a given server.

        Args:
          channel_args: Required. The channel args used for server.

        Returns:
          True if this this plugin option is active on the server, false otherwise.
        """
        return True

    def get_label_injector(self) -> Optional[OpenTelemetryLabelInjector]:
        # Returns the LabelsInjector used by this plugin option, or None.
        return CSMOpenTelemetryLabelInjector()


# pylint: disable=no-self-use
class CSMOpenTelemetryPlugin(OpenTelemetryPlugin):
    """Describes a Plugin for OpenTelemetry observability.

    This is class is part of an EXPERIMENTAL API.
    """

    def get_plugin_options(
        self,
    ) -> Iterable[OpenTelemetryPluginOption]:
        return [CSMOpenTelemetryPluginOption()]


# pylint: disable=no-self-use
class _CSMOpenTelemetryPlugin(CSMOpenTelemetryPlugin):
    """Describes a Plugin for OpenTelemetry observability.

    This is class is part of an EXPERIMENTAL API.
    """

    def get_meter_provider(self) -> Optional[MeterProvider]:
        # This should return a StackDriver MeterProvider
        return None