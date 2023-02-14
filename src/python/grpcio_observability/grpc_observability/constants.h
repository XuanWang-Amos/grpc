// Copyright 2023 gRPC authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <string>

namespace grpc_observability {

const std::string kClientMethod = "grpc_client_method";
const std::string kClientStatus = "grpc_client_status";
const std::string kServerMethod = "grpc_server_method";
const std::string kServerStatus = "grpc_server_status";

typedef enum {
  kMeasurementDouble = 0,
  kMeasurementInt
} MeasurementType;

typedef enum {
  kSpanData = 0,
  kMetricData
} DataType;

// Client

typedef enum {
    kRpcClientSentMessagesPerRpcMeasureName = 0,
    kRpcClientSentBytesPerRpcMeasureName,
    kRpcClientReceivedMessagesPerRpcMeasureName,
    kRpcClientReceivedBytesPerRpcMeasureName,
    kRpcClientRoundtripLatencyMeasureName,
    kRpcClientServerLatencyMeasureName,
    kRpcClientStartedRpcsMeasureName,
    kRpcClientRetriesPerCallMeasureName,
    kRpcClientTransparentRetriesPerCallMeasureName,
    kRpcClientRetryDelayPerCallMeasureName,
    kRpcClientTransportLatencyMeasureName,
    kRpcServerSentMessagesPerRpcMeasureName,
    kRpcServerSentBytesPerRpcMeasureName,
    kRpcServerReceivedMessagesPerRpcMeasureName,
    kRpcServerReceivedBytesPerRpcMeasureName,
    kRpcServerServerLatencyMeasureName,
    kRpcServerStartedRpcsMeasureName
} MetricsName;

// const std::string
//     kRpcClientSentMessagesPerRpcMeasureName =
//         "grpc.io/client/sent_messages_per_rpc";

// const std::string kRpcClientSentBytesPerRpcMeasureName =
//     "grpc.io/client/sent_bytes_per_rpc";

// const std::string
//     kRpcClientReceivedMessagesPerRpcMeasureName =
//         "grpc.io/client/received_messages_per_rpc";

// const std::string
//     kRpcClientReceivedBytesPerRpcMeasureName =
//         "grpc.io/client/received_bytes_per_rpc";

// const std::string kRpcClientRoundtripLatencyMeasureName =
//     "grpc.io/client/roundtrip_latency";

// const std::string kRpcClientServerLatencyMeasureName =
//     "grpc.io/client/server_latency";

// const std::string kRpcClientStartedRpcsMeasureName =
//     "grpc.io/client/started_rpcs";

// const std::string kRpcClientRetriesPerCallMeasureName =
//     "grpc.io/client/retries_per_call";

// const std::string
//     kRpcClientTransparentRetriesPerCallMeasureName =
//         "grpc.io/client/transparent_retries_per_call";

// const std::string kRpcClientRetryDelayPerCallMeasureName =
//     "grpc.io/client/retry_delay_per_call";

// const std::string kRpcClientTransportLatencyMeasureName =
//     "grpc.io/client/transport_latency";

// // Server
// const std::string
//     kRpcServerSentMessagesPerRpcMeasureName =
//         "grpc.io/server/sent_messages_per_rpc";

// const std::string kRpcServerSentBytesPerRpcMeasureName =
//     "grpc.io/server/sent_bytes_per_rpc";

// const std::string
//     kRpcServerReceivedMessagesPerRpcMeasureName =
//         "grpc.io/server/received_messages_per_rpc";

// const std::string
//     kRpcServerReceivedBytesPerRpcMeasureName =
//         "grpc.io/server/received_bytes_per_rpc";

// const std::string kRpcServerServerLatencyMeasureName =
//     "grpc.io/server/server_latency";

// const std::string kRpcServerStartedRpcsMeasureName =
//     "grpc.io/server/started_rpcs";

}

#endif // CONSTANTS_H