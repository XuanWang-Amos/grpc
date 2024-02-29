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
from typing import AnyStr, Dict, Iterable, List, Optional, Union

# pytype: disable=pyi-error
import grpc
from grpc_observability import _open_telemetry_measures
from grpc_observability._cyobservability import MetricsName
from grpc_observability._observability import StatsData
from grpc_observability._observability import OptionalLabelType
from opentelemetry.metrics import Counter
from opentelemetry.metrics import Histogram
from opentelemetry.metrics import Meter
from opentelemetry.metrics import MeterProvider

GRPC_METHOD_LABEL = "grpc.method"
GRPC_TARGET_LABEL = "grpc.target"
GRPC_OTHER_LABEL_VALUE = "other"


class OpenTelemetryLabelInjector(abc.ABC):
    """
    An interface that allows you to add additional labels on the calls traced.

    Please note that this class is still work in progress and NOT READY to be used.
    """

    @abc.abstractmethod
    def get_labels_for_exchange(self) -> Dict[str, AnyStr]:
        """
        Get labels used for metadata exchange.

        Returns:
          A dict of labels.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_additional_label(self) -> Dict[str, str]:
        """
        Get additional labels added by this injector.

        Returns:
          A dict of labels.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def maybe_deserialize_labels(self, labels: Dict[str, AnyStr]) -> Dict[str, str]:
        """
        Deserialize the labels if the label is serialized and added by this injector.

        Returns:
          A dict of deserialized labels.
        """
        raise NotImplementedError()


class OpenTelemetryPluginOption(abc.ABC):
    """
    An interface that allows you to add additional function to OpenTelemetryPlugin.

    Please note that this class is still work in progress and NOT READY to be used.
    """


# pylint: disable=no-self-use
class OpenTelemetryPlugin:
    """Describes a Plugin for OpenTelemetry observability.

    This is class is part of an EXPERIMENTAL API.
    """

    def _get_plugin_options(
        self,
    ) -> Iterable[OpenTelemetryPluginOption]:
        """
        This is a private method.

        This function will be used to get plugin options which are enabled for
        this OpenTelemetryPlugin instance.

        Returns:
            An Iterable of class OpenTelemetryPluginOption which will be enabled for
            this OpenTelemetryPlugin.
        """
        return []

    def get_meter_provider(self) -> Optional[MeterProvider]:
        """
        This function will be used to get the MeterProvider for this OpenTelemetryPlugin
        instance.

        Returns:
            A MeterProvider which will be used to collect telemetry data, or None which
            means no metrics will be collected.
        """
        return None

    def target_attribute_filter(
        self, target: str  # pylint: disable=unused-argument
    ) -> bool:
        """
        Once overridden, this will be called per channel to decide whether to record the
        target attribute on client or to replace it with "other".
        This helps reduce the cardinality on metrics in cases where many channels
        are created with different targets in the same binary (which might happen
        for example, if the channel target string uses IP addresses directly).

        Args:
            target: The target for the RPC.

        Returns:
            bool: True means the original target string will be used, False means target string
            will be replaced with "other".
        """
        return True

    def generic_method_attribute_filter(
        self, method: str  # pylint: disable=unused-argument
    ) -> bool:
        """
        Once overridden, this will be called with a generic method type to decide whether to
        record the method name or to replace it with "other".

        Note that pre-registered methods will always be recorded no matter what this
        function returns.

        Args:
            method: The method name for the RPC.

        Returns:
            bool: True means the original method name will be used, False means method name
            will be replaced with "other".
        """
        return False

    def _get_enabled_optional_labels(self) -> List[OptionalLabelType]:
        return []


class _OpenTelemetryPlugin:
    _plugin: OpenTelemetryPlugin
    _metric_to_recorder: Dict[MetricsName, Union[Counter, Histogram]]
    identifier: str

    def __init__(self, plugin: OpenTelemetryPlugin):
        self._plugin = plugin
        self._metric_to_recorder = dict()
        self.identifier = str(id(self))

        meter_provider = self._plugin.get_meter_provider()
        if meter_provider:
            meter = meter_provider.get_meter("grpc-python", grpc.__version__)
            enabled_metrics = _open_telemetry_measures.base_metrics()
            self._metric_to_recorder = self._register_metrics(meter, enabled_metrics)

    def _should_record(self, stats_data: StatsData) -> bool:
        # Decide if this plugin should record the stats_data.
        return stats_data.name in self._metric_to_recorder.keys()

    def _record_stats_data(self, stats_data: StatsData) -> None:
        recorder = self._metric_to_recorder[stats_data.name]
        deserialized_labels = self._maybe_deserialize_labels(stats_data.labels)
        labels = self._maybe_add_labels(deserialized_labels)
        decoded_labels = self.decode_labels(labels)

        target = decoded_labels.get(GRPC_TARGET_LABEL, "")
        if not self._plugin.target_attribute_filter(target):
            # Filter target name.
            decoded_labels[GRPC_TARGET_LABEL] = GRPC_OTHER_LABEL_VALUE

        method = decoded_labels.get(GRPC_METHOD_LABEL, "")
        if not self._plugin.generic_method_attribute_filter(method):
            # Filter method name.
            decoded_labels[GRPC_METHOD_LABEL] = GRPC_OTHER_LABEL_VALUE

        value = 0
        if stats_data.measure_double:
            value = stats_data.value_float
        else:
            value = stats_data.value_int
        if isinstance(recorder, Counter):
            recorder.add(value, attributes=decoded_labels)
        elif isinstance(recorder, Histogram):
            recorder.record(value, attributes=decoded_labels)

    # pylint: disable=no-self-use
    def maybe_record_stats_data(self, stats_data: List[StatsData]) -> None:
        # Records stats data to MeterProvider.
        if self._should_record(stats_data):
            self._record_stats_data(stats_data)

    def get_client_exchange_labels(self, target: bytes) -> Dict[str, AnyStr]:
        labels_for_exchange = {}
        target_str = target.decode("utf-8", "replace")
        for plugin_option in self._plugin._get_plugin_options():
            if all([
                hasattr(plugin_option, "is_active_on_client_channel"),
                plugin_option.is_active_on_client_channel(target_str),
                hasattr(plugin_option, "get_label_injector"),
                hasattr(plugin_option.get_label_injector(), "get_labels_for_exchange"),
            ]):
                labels_for_exchange.update(
                    plugin_option.get_label_injector().get_labels_for_exchange()
                )
        return labels_for_exchange

    def get_server_exchange_labels(self, xds: bool) -> Dict[str, str]:
        labels_for_exchange = {}
        for plugin_option in self._plugin._get_plugin_options():
            if all([
                hasattr(plugin_option, "is_active_on_server"),
                plugin_option.is_active_on_server(xds),
                hasattr(plugin_option, "get_label_injector"),
                hasattr(plugin_option.get_label_injector(), "get_labels_for_exchange"),
            ]):
                labels_for_exchange.update(
                    plugin_option.get_label_injector().get_labels_for_exchange()
                )
        return labels_for_exchange

    def _maybe_deserialize_labels(self, labels: Dict[str, AnyStr]) -> Dict[str, AnyStr]:
        for plugin_option in self._plugin._get_plugin_options():
            if all([
                hasattr(plugin_option, "get_label_injector"),
                hasattr(plugin_option.get_label_injector(), "maybe_deserialize_labels"),
            ]):
                labels = plugin_option.get_label_injector().maybe_deserialize_labels(labels)
        return labels

    def _maybe_add_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        for plugin_option in self._plugin._get_plugin_options():
            if all([
                hasattr(plugin_option, "get_label_injector"),
                hasattr(plugin_option.get_label_injector(), "get_additional_label"),
            ]):
                labels.update(plugin_option.get_label_injector().get_additional_label())
        return labels

    def get_enabled_optional_labels(self) -> List[OptionalLabelType]:
        return self._plugin._get_enabled_optional_labels()

    def _register_metrics(
        self, meter: Meter, metrics: List[_open_telemetry_measures.Metric]
    ) -> Dict[MetricsName, Union[Counter, Histogram]]:
        metric_to_recorder_map = {}
        recorder = None
        for metric in metrics:
            if metric == _open_telemetry_measures.CLIENT_ATTEMPT_STARTED:
                recorder = meter.create_counter(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.CLIENT_ATTEMPT_DURATION:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.CLIENT_RPC_DURATION:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.CLIENT_ATTEMPT_SEND_BYTES:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.CLIENT_ATTEMPT_RECEIVED_BYTES:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.SERVER_STARTED_RPCS:
                recorder = meter.create_counter(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.SERVER_RPC_DURATION:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.SERVER_RPC_SEND_BYTES:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            elif metric == _open_telemetry_measures.SERVER_RPC_RECEIVED_BYTES:
                recorder = meter.create_histogram(
                    name=metric.name,
                    unit=metric.unit,
                    description=metric.description,
                )
            metric_to_recorder_map[metric.cyname] = recorder
        return metric_to_recorder_map

    def decode_labels(self, labels: Dict[str, AnyStr]) -> Dict[str, str]:
        decoded_labels = {}
        for key, value in labels.items():
            if isinstance(value, bytes):
                value = value.decode()
            decoded_labels[key] = value
        return decoded_labels
