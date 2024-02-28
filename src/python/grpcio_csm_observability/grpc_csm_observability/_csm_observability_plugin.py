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
import json
import os
from typing import AnyStr, Dict, Iterable, List, Optional, Union

# pytype: disable=pyi-error
from grpc_observability import _open_telemetry_measures
from grpc_observability._cyobservability import MetricsName
from grpc_observability._observability import StatsData
from grpc_observability._observability import OptionalLabelType
from grpc_observability._open_telemetry_plugin import OpenTelemetryPlugin
from grpc_observability._open_telemetry_plugin import _OpenTelemetryPlugin
from grpc_observability._open_telemetry_plugin import OpenTelemetryLabelInjector
from grpc_observability._open_telemetry_plugin import OpenTelemetryPluginOption
from opentelemetry.metrics import Counter
from opentelemetry.metrics import Histogram
from opentelemetry.metrics import Meter
from opentelemetry.metrics import MeterProvider

from opentelemetry.sdk.resources import Resource, get_aggregated_resources
# from opentelemetry.tools.resource_detector import GoogleCloudResourceDetector
from opentelemetry.resourcedetector.gcp_resource_detector import GoogleCloudResourceDetector
from opentelemetry.semconv.resource import ResourceAttributes
from google.protobuf import struct_pb2

GRPC_METHOD_LABEL = "grpc.method"
GRPC_TARGET_LABEL = "grpc.target"
GRPC_OTHER_LABEL_VALUE = "other"
UNKNOWN_VALUE = "unknown"
TYPE_GCE = "gcp_compute_engine"
TYPE_GKE = "gcp_kubernetes_engine"

METADATA_EXCHANGE_KEY_FIXED_MAP = {
    "type": "csm.remote_workload_type",
    "canonical_service": "csm.remote_workload_canonical_service",
}
METADATA_EXCHANGE_KEY_GKE_MAP = {
    "workload_name": "csm.remote_workload_name",
    "namespace_name": "csm.remote_workload_namespace_name",
    "cluster_name": "csm.remote_workload_cluster_name",
    "location": "csm.remote_workload_location",
    "project_id": "csm.remote_workload_project_id",
}
METADATA_EXCHANGE_KEY_GCE_MAP = {
    "workload_name": "csm.remote_workload_name",
    "location": "csm.remote_workload_type",
    "project_id": "csm.remote_workload_type",
}


class CSMOpenTelemetryLabelInjector(OpenTelemetryLabelInjector):
    """
    An interface that allows you to add additional labels on the calls traced.

    Please note that this class is still work in progress and NOT READY to be used.
    """

    _exchange_labels: Dict[str, AnyStr]
    _local_labels: Dict[str, str]

    def __init__(self, is_client=False):
        # Calls Python OTel API to detect resource and get labels, save
        # those lables to OpenTelemetryLabelInjector.labels.
        fields = {}
        self._exchange_labels = {}
        self._local_labels = {}

        prefix = ""
        _type = ""
        # print(f"is_client={is_client}")
        if is_client:
            prefix = "[Client]"
            _type = "GCE"
        else:
            prefix = "[Server]"
            _type = "GKE"
        # print(f"prefix={prefix}")

        # fields["type"] = struct_pb2.Value(string_value=f"{prefix}{_type}")
        # fields["canonical_service"] = struct_pb2.Value(
        #     string_value=f"{prefix}canonical_service"
        # )
        # if _type == "GKE":
        #     fields["workload_name"] = struct_pb2.Value(
        #         string_value=f"{prefix}workload_name"
        #     )
        #     fields["namespace_name"] = struct_pb2.Value(
        #         string_value=f"{prefix}namespace_name"
        #     )
        #     fields["cluster_name"] = struct_pb2.Value(
        #         string_value=f"{prefix}cluster_name"
        #     )
        #     fields["location"] = struct_pb2.Value(string_value=f"{prefix}location")
        #     fields["project_id"] = struct_pb2.Value(string_value=f"{prefix}project_id")
        # else:
        #     fields["workload_name"] = struct_pb2.Value(
        #         string_value=f"{prefix}workload_name"
        #     )
        #     fields["location"] = struct_pb2.Value(string_value=f"{prefix}location")
        #     fields["project_id"] = struct_pb2.Value(string_value=f"{prefix}project_id")

        resource = get_aggregated_resources([GoogleCloudResourceDetector()])
        type_value = self._get_str_value_from_resource(ResourceAttributes.CLOUD_PLATFORM, resource)
        canonical_service_value = os.getenv("CSM_CANONICAL_SERVICE_NAME", UNKNOWN_VALUE)
        workload_name_value = os.getenv("CSM_WORKLOAD_NAME", UNKNOWN_VALUE)
        namespace_value = self._get_str_value_from_resource(ResourceAttributes.K8S_NAMESPACE_NAME, resource)
        cluster_name_value = self._get_str_value_from_resource(ResourceAttributes.K8S_CLUSTER_NAME, resource)
        location_value = self._get_str_value_from_resource(ResourceAttributes.CLOUD_AVAILABILITY_ZONE, resource)
        if (UNKNOWN_VALUE == location_value):
            location_value = self._get_str_value_from_resource(ResourceAttributes.CLOUD_REGION, resource)
        project_id_value = self._get_str_value_from_resource(ResourceAttributes.CLOUD_ACCOUNT_ID, resource)

        fields["type"] = struct_pb2.Value(string_value=type_value)
        fields["canonical_service"] = struct_pb2.Value(string_value=canonical_service_value)
        if type_value == "GKE":
            fields["workload_name"] = struct_pb2.Value(string_value=workload_name_value)
            fields["namespace_name"] = struct_pb2.Value(string_value=namespace_value)
            fields["cluster_name"] = struct_pb2.Value(string_value=cluster_name_value)
            fields["location"] = struct_pb2.Value(string_value=location_value)
            fields["project_id"] = struct_pb2.Value(string_value=project_id_value)
        else:
            fields["workload_name"] = struct_pb2.Value(string_value=workload_name_value)
            fields["location"] = struct_pb2.Value(string_value=location_value)
            fields["project_id"] = struct_pb2.Value(string_value=project_id_value)

        serialized_struct = struct_pb2.Struct(fields=fields)
        serialized_str = serialized_struct.SerializeToString()

        self._exchange_labels = {"XEnvoyPeerMetadata": serialized_str}
        self._local_labels["csm.workload_canonical_service"] = canonical_service_value
        self._local_labels["csm.mesh_id"] = self._get_mesh_id()

    def get_exchange_labels(self) -> Dict[str, AnyStr]:
        return self._exchange_labels

    def add_and_deserialize_labels(self, labels: Dict[str, AnyStr]) -> Dict[str, str]:
        new_labels = {}
        for key, value in labels.items():
            if "XEnvoyPeerMetadata" == key:
                struct = struct_pb2.Struct()
                struct.ParseFromString(value)

                remote_type = self._get_value_from_struct("type", struct)

                for key, remote_key in METADATA_EXCHANGE_KEY_FIXED_MAP.items():
                    new_labels[remote_key] = self._get_value_from_struct(key, struct)

                if TYPE_GCE in remote_type:
                    for key, remote_key in METADATA_EXCHANGE_KEY_GKE_MAP.items():
                        new_labels[remote_key] = self._get_value_from_struct(
                            key, struct
                        )
                else:
                    for key, remote_key in METADATA_EXCHANGE_KEY_GCE_MAP.items():
                        new_labels[remote_key] = self._get_value_from_struct(
                            key, struct
                        )
            else:
                new_labels[key] = value

        new_labels.update(self._local_labels)
        return new_labels

    def _get_value_from_struct(self, key: str, struct: struct_pb2.Struct) -> str:
        value = struct.fields.get(key)
        if not value:
            return UNKNOWN_VALUE
        return value.string_value

    def _get_str_value_from_resource(self, attribute: ResourceAttributes, resource: Resource) -> str:
        value = resource.attributes.get(attribute, UNKNOWN_VALUE)
        return str(value)

    # Returns the mesh ID by reading and parsing the bootstrap file. Returns "unknown"
    # if for some reason, mesh ID could not be figured out.
    def _get_mesh_id(self) -> str:
        config_contents = self._get_bootstrap_config_contents()

        try:
            config_json = json.loads(config_contents)
            # The expected format of the Node ID is -
            # projects/[GCP Project number]/networks/mesh:[Mesh ID]/nodes/[UUID]
            node_id_parts = config_json.get("node", {}).get("id", "").split("/")
            if len(node_id_parts) == 6 and "mesh:" in node_id_parts[3]:
                return node_id_parts[3].removeprefix("mesh:")
        except json.decoder.JSONDecodeError:
            return UNKNOWN_VALUE

        return UNKNOWN_VALUE

    def _get_bootstrap_config_contents(self) -> str:
        """Get the contents of the bootstrap config from environment variable or file.

        Returns:
            The content from environment variable. Or empty str if no config was found.
        """
        contents_str = ""
        for source in ("GRPC_XDS_BOOTSTRAP", "GRPC_XDS_BOOTSTRAP_CONFIG"):
            config = os.getenv(source)
            if config:
                if os.path.isfile(config):  # Prioritize file over raw config
                    with open(config, "r") as f:
                        contents_str = f.read()
                else:
                    contents_str = config

        return contents_str


class CsmOpenTelemetryPluginOption(OpenTelemetryPluginOption):
    """
    An interface that allows you to add additional function to OpenTelemetryPlugin.

    Please note that this class is still work in progress and NOT READY to be used.
    """

    def is_active_on_client_channel(self, target: str) -> bool:
        """Determines whether this plugin option is active on a channel based on target.

        Args:
          method: Required. The target for the RPC.

        Returns:
          True if this this plugin option is active on the channel, false otherwise.
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

    def get_server_label_injector(self) -> Optional[OpenTelemetryLabelInjector]:
        # Returns the LabelsInjector used by this plugin option, or None.
        return CSMOpenTelemetryLabelInjector(is_client=False)

    def get_client_label_injector(self) -> Optional[OpenTelemetryLabelInjector]:
        # Returns the LabelsInjector used by this plugin option, or None.
        return CSMOpenTelemetryLabelInjector(is_client=True)


# pylint: disable=no-self-use
class CsmOpenTelemetryPlugin(OpenTelemetryPlugin):
    """Describes a Plugin for OpenTelemetry observability.

    This is class is part of an EXPERIMENTAL API.
    """

    def _get_plugin_options(
        self,
    ) -> Iterable[OpenTelemetryPluginOption]:
        return [CsmOpenTelemetryPluginOption()]

    def _get_enabled_optional_labels(self) -> List[OptionalLabelType]:
        return [OptionalLabelType.XDS_SERVICE_LABELS]


# pylint: disable=no-self-use
class _CsmOpenTelemetryPlugin(CsmOpenTelemetryPlugin):
    """Describes a Plugin for OpenTelemetry observability.

    This is class is part of an EXPERIMENTAL API.
    """

    def get_meter_provider(self) -> Optional[MeterProvider]:
        # This should return a StackDriver MeterProvider
        return None
