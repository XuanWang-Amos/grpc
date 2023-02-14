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

from opencensus.stats import measure as measure_module

# These measure definitions should be kept in sync across opencensus implementations.
# https://github.com/census-instrumentation/opencensus-java/blob/master/contrib/grpc_metrics/src/main/java/io/opencensus/contrib/grpc/metrics/RpcMeasureConstants.java.

# Unit constatns
UNIT_BYTES = "By"
UNIT_MILLISECONDS = "ms"
UNIT_COUNT = "1"


# Client
def rpc_client_send_bytes_per_prc() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/client/sent_bytes_per_rpc",
        "Total bytes sent across all request messages per RPC", UNIT_BYTES)


def rpc_client_received_bytes_per_rpc() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/client/received_bytes_per_rpc",
        "Total bytes received across all response messages per RPC", UNIT_BYTES)


def rpc_client_roundtrip_latency() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/client/roundtrip_latency",
        "Time between first byte of request sent to last byte of response received, or terminal error",
        UNIT_MILLISECONDS)


def rpc_client_completed_rpcs() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/client/completed_rpcs",
        "The total number of completed client RPCs", UNIT_COUNT)


def rpc_client_server_latency() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/client/server_latency",
        "Time between first byte of request received to last byte of response sent, or terminal error (propagated from the server)",
        UNIT_MILLISECONDS)


def rpc_client_sent_messages_per_rpc() -> measure_module.MeasureInt:
    return measure_module.MeasureInt("grpc.io/client/sent_messages_per_rpc",
                                     "Number of messages sent per RPC",
                                     UNIT_COUNT)


def rpc_client_received_messages_per_rpc() -> measure_module.MeasureInt:
    return measure_module.MeasureInt("grpc.io/client/received_messages_per_rpc",
                                     "Number of messages received per RPC",
                                     UNIT_COUNT)


def rpc_client_started_rpcs() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/client/started_rpcs",
        "The total number of client RPCs ever opened, including those that have not been completed.",
        UNIT_COUNT)


def rpc_client_transport_latency() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/client/transport_latency",
        "Time between first byte of request sent to last byte of response received on the transport",
        UNIT_MILLISECONDS)


# Client per-overall-client-call measures
def rpc_client_retries_per_call() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/client/retries_per_call",
        "Number of retry or hedging attempts excluding transparent retries made during the client call",
        UNIT_COUNT)


def rpc_client_transparent_retries_per_call() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/client/transparent_retries_per_call",
        "Number of transparent retries made during the client call", UNIT_COUNT)


def rpc_client_retry_delay_per_call() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/client/retry_delay_per_call",
        "Total time of delay while there is no active attempt during the client call",
        UNIT_MILLISECONDS)


# Server
def rpc_server_sent_bytes_per_rpc() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/server/sent_bytes_per_rpc",
        "Total bytes sent across all messages per RPC", UNIT_BYTES)


def rpc_server_received_bytes_per_rpc() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/server/received_bytes_per_rpc",
        "Total bytes received across all messages per RPC", UNIT_BYTES)


def rpc_server_server_latency() -> measure_module.MeasureFloat:
    return measure_module.MeasureFloat(
        "grpc.io/server/server_latency",
        "Time between first byte of request received to last byte of response sent, or terminal error",
        UNIT_MILLISECONDS)


def rpc_server_completed_rpcs() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/server/completed_rpcs",
        "The total number of completed server RPCs", UNIT_COUNT)


def rpc_server_started_rpcs() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/server/started_rpcs",
        "Total bytes sent across all request messages per RPC", UNIT_COUNT)


def rpc_server_sent_messages_per_rpc() -> measure_module.MeasureInt:
    return measure_module.MeasureInt("grpc.io/server/sent_messages_per_rpc",
                                     "Number of messages sent per RPC",
                                     UNIT_COUNT)


def rpc_server_received_messages_per_rpc() -> measure_module.MeasureInt:
    return measure_module.MeasureInt(
        "grpc.io/server/received_messages_per_rpc",
        "The total number of server RPCs ever opened, including those that have not been completed.",
        UNIT_COUNT)
