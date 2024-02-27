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

#include <grpc/support/port_platform.h>

#include "server_call_tracer.h"

#include <stdint.h>
#include <string.h>

#include <algorithm>
#include <initializer_list>
#include <string>
#include <utility>
#include <vector>

#include "absl/strings/escaping.h"
#include "absl/strings/str_cat.h"
#include "absl/strings/str_format.h"
#include "absl/strings/string_view.h"
#include "absl/time/clock.h"
#include "absl/time/time.h"
#include "constants.h"
#include "observability_util.h"
#include "python_census_context.h"

#include "src/core/lib/channel/call_tracer.h"
#include "src/core/lib/channel/channel_stack.h"
#include "src/core/lib/iomgr/error.h"
#include "src/core/lib/resource_quota/arena.h"
#include "src/core/lib/slice/slice.h"
#include "src/core/lib/slice/slice_buffer.h"
#include "src/core/lib/transport/metadata_batch.h"

namespace grpc_observability {

namespace {

// server metadata elements
struct ServerO11yMetadata {
  grpc_core::Slice path;
  grpc_core::Slice tracing_slice;
  grpc_core::Slice census_proto;
};

void GetO11yMetadata(const grpc_metadata_batch* b, ServerO11yMetadata* som) {
  const auto* path = b->get_pointer(grpc_core::HttpPathMetadata());
  if (path != nullptr) {
    som->path = path->Ref();
  }
  if (PythonCensusTracingEnabled()) {
    const auto* grpc_trace_bin =
        b->get_pointer(grpc_core::GrpcTraceBinMetadata());
    if (grpc_trace_bin != nullptr) {
      som->tracing_slice = grpc_trace_bin->Ref();
    }
  }
  if (PythonCensusStatsEnabled()) {
    const auto* grpc_tags_bin =
        b->get_pointer(grpc_core::GrpcTagsBinMetadata());
    if (grpc_tags_bin != nullptr) {
      som->census_proto = grpc_tags_bin->Ref();
    }
  }
}

}  // namespace

//
// PythonOpenCensusServerCallTracer
//

void PythonOpenCensusServerCallTracer::RecordSendInitialMetadata(
      grpc_metadata_batch* send_initial_metadata) {
    // 1. Check if incoming metadata have x-envoy-peer-metadata label.
    // 2. If it does, perform metadata exchange.
    // 3. send_initial_metadata->Set(grpc_core::XEnvoyPeerMetadata(), 
    labels_injector_.ServerAddLabels(send_initial_metadata, injected_labels_);
    // serialized_labels_to_send_.Ref())
    // serialized_labels_to_send_
    // active_plugin_options_view_.ForEach(
    //     [&](const InternalOpenTelemetryPluginOption& plugin_option,
    //         size_t index) {
    //       auto* labels_injector = plugin_option.labels_injector();
    //       if (labels_injector != nullptr) {
    //         labels_injector->AddLabels(
    //             send_initial_metadata,
    //             injected_labels_from_plugin_options_[index].get());
    //       }
    //       return true;
    //     });
}

void PythonOpenCensusServerCallTracer::RecordReceivedInitialMetadata(
    grpc_metadata_batch* recv_initial_metadata) {
  ServerO11yMetadata som;
  GetO11yMetadata(recv_initial_metadata, &som);
  path_ = std::move(som.path);
  method_ = GetMethod(path_);
  auto tracing_enabled = PythonCensusTracingEnabled();
  GenerateServerContext(
      tracing_enabled ? som.tracing_slice.as_string_view() : "",
      absl::StrCat("Recv.", method_), &context_);
  if (PythonCensusStatsEnabled()) {
    context_.Labels().emplace_back(kServerMethod, std::string(method_));
    // std::cout << "[CALLTRACER][Server] Adding data with identifier RecordReceivedInitialMetadata: " << identifier_ << std::endl;
    RecordIntMetric(kRpcServerStartedRpcsMeasureName, 1, context_.Labels(), identifier_);
  }

  // C++ GetLabels returns metadata_label + local_label
  // Python GetLabels returns metadata_label + additional_labels
  injected_labels_ = labels_injector_.GetLabels(recv_initial_metadata);

  // for (const auto& label : injected_labels_) {
  //     std::cout << "[SERVER] labels from peer: " << label.key << ": " << label.value << std::endl;
  //     context_.Labels().emplace_back(label);
  // }

  // path_ =
  //     recv_initial_metadata->get_pointer(grpc_core::HttpPathMetadata())->Ref();
  // active_plugin_options_view_.ForEach(
  //     [&](const InternalOpenTelemetryPluginOption& plugin_option,
  //         size_t index) {
  //       auto* labels_injector = plugin_option.labels_injector();
  //       if (labels_injector != nullptr) {
  //         injected_labels_from_plugin_options_[index] =
  //             labels_injector->GetLabels(recv_initial_metadata);
  //       }
  //       return true;
  //     });
  // registered_method_ =
  //     recv_initial_metadata->get(grpc_core::GrpcRegisteredMethod())
  //         .value_or(nullptr) != nullptr;
  // std::array<std::pair<absl::string_view, absl::string_view>, 1>
  //     additional_labels = {{{OpenTelemetryMethodKey(), MethodForStats()}}};
  // if (OpenTelemetryPluginState().server.call.started != nullptr) {
  //   // We might not have all the injected labels that we want at this point, so
  //   // avoid recording a subset of injected labels here.
  //   OpenTelemetryPluginState().server.call.started->Add(
  //       1, KeyValueIterable(/*injected_labels_from_plugin_options=*/{},
  //                           additional_labels,
  //                           /*active_plugin_options_view=*/nullptr, {},
  //                           /*is_client=*/false));
  // }
}

void PythonOpenCensusServerCallTracer::RecordSendTrailingMetadata(
    grpc_metadata_batch* send_trailing_metadata) {
  // We need to record the time when the trailing metadata was sent to
  // mark the completeness of the request.
  elapsed_time_ = absl::Now() - start_time_;
  if (PythonCensusStatsEnabled() && send_trailing_metadata != nullptr) {
    size_t len = ServerStatsSerialize(absl::ToInt64Nanoseconds(elapsed_time_),
                                      stats_buf_, kMaxServerStatsLen);
    if (len > 0) {
      send_trailing_metadata->Set(
          grpc_core::GrpcServerStatsBinMetadata(),
          grpc_core::Slice::FromCopiedBuffer(stats_buf_, len));
    }
  }
}

void PythonOpenCensusServerCallTracer::RecordSendMessage(const grpc_core::SliceBuffer& send_message) {
    RecordAnnotation(
        absl::StrFormat("Send message: %ld bytes", send_message.Length()));
    ++sent_message_count_;
}

void PythonOpenCensusServerCallTracer::RecordSendCompressedMessage(
      const grpc_core::SliceBuffer& send_compressed_message) {
    RecordAnnotation(absl::StrFormat("Send compressed message: %ld bytes",
                                     send_compressed_message.Length()));
}

void PythonOpenCensusServerCallTracer::RecordReceivedMessage(
      const grpc_core::SliceBuffer& recv_message) {
    RecordAnnotation(
        absl::StrFormat("Received message: %ld bytes", recv_message.Length()));
    ++recv_message_count_;
}

void PythonOpenCensusServerCallTracer::RecordReceivedDecompressedMessage(
      const grpc_core::SliceBuffer& recv_decompressed_message) {
    RecordAnnotation(absl::StrFormat("Received decompressed message: %ld bytes",
                                     recv_decompressed_message.Length()));
}

void PythonOpenCensusServerCallTracer::RecordCancel(grpc_error_handle /*cancel_error*/) {
    elapsed_time_ = absl::Now() - start_time_;
}

void PythonOpenCensusServerCallTracer::RecordEnd(
    const grpc_call_final_info* final_info) {
  if (PythonCensusStatsEnabled()) {
    const uint64_t request_size = GetOutgoingDataSize(final_info);
    const uint64_t response_size = GetIncomingDataSize(final_info);
    double elapsed_time_s = absl::ToDoubleSeconds(elapsed_time_);
    context_.Labels().emplace_back(kServerMethod, std::string(method_));
    context_.Labels().emplace_back(
        kServerStatus,
        std::string(StatusCodeToString(final_info->final_status)));
    for (const auto& label : injected_labels_) {
        // std::cout << "[SERVER] labels from peer: " << label.key << ": " << label.value << std::endl;
        context_.Labels().emplace_back(label);
    }
    // std::cout << "[CALLTRACER][Server] Adding data with identifier RecordEnd: " << identifier_ << std::endl;
    RecordDoubleMetric(kRpcServerSentBytesPerRpcMeasureName,
                       static_cast<double>(response_size), context_.Labels(), identifier_);
    RecordDoubleMetric(kRpcServerReceivedBytesPerRpcMeasureName,
                       static_cast<double>(request_size), context_.Labels(), identifier_);
    RecordDoubleMetric(kRpcServerServerLatencyMeasureName, elapsed_time_s,
                       context_.Labels(), identifier_);
    RecordIntMetric(kRpcServerCompletedRpcMeasureName, 1, context_.Labels(), identifier_);
    RecordIntMetric(kRpcServerSentMessagesPerRpcMeasureName,
                    sent_message_count_, context_.Labels(), identifier_);
    RecordIntMetric(kRpcServerReceivedMessagesPerRpcMeasureName,
                    recv_message_count_, context_.Labels(), identifier_);
  }
  if (PythonCensusTracingEnabled()) {
    context_.EndSpan();
    if (IsSampled()) {
      RecordSpan(context_.GetSpan().ToCensusData());
    }
  }

  // std::array<std::pair<absl::string_view, absl::string_view>, 2>
  //     additional_labels = {
  //         {{OpenTelemetryMethodKey(), MethodForStats()},
  //          {OpenTelemetryStatusKey(),
  //           grpc_status_code_to_string(final_info->final_status)}}};
  // // Currently we do not have any optional labels on the server side.
  // KeyValueIterable labels(
  //     injected_labels_from_plugin_options_, additional_labels,
  //     /*active_plugin_options_view=*/nullptr, /*optional_labels_span=*/{},
  //     /*is_client=*/false);
  // if (OpenTelemetryPluginState().server.call.duration != nullptr) {
  //   OpenTelemetryPluginState().server.call.duration->Record(
  //       absl::ToDoubleSeconds(elapsed_time_), labels,
  //       opentelemetry::context::Context{});
  // }
  // if (OpenTelemetryPluginState()
  //         .server.call.sent_total_compressed_message_size != nullptr) {
  //   OpenTelemetryPluginState()
  //       .server.call.sent_total_compressed_message_size->Record(
  //           final_info->stats.transport_stream_stats.outgoing.data_bytes,
  //           labels, opentelemetry::context::Context{});
  // }
  // if (OpenTelemetryPluginState()
  //         .server.call.rcvd_total_compressed_message_size != nullptr) {
  //   OpenTelemetryPluginState()
  //       .server.call.rcvd_total_compressed_message_size->Record(
  //           final_info->stats.transport_stream_stats.incoming.data_bytes,
  //           labels, opentelemetry::context::Context{});
  // }
  // After RecordEnd, Core will make no further usage of this ServerCallTracer,
  // so we are free it here.
  delete this;
}

void PythonOpenCensusServerCallTracer::RecordAnnotation(absl::string_view annotation) {
    if (!context_.GetSpanContext().IsSampled()) {
      return;
    }
    context_.AddSpanAnnotation(annotation);
}

void PythonOpenCensusServerCallTracer::RecordAnnotation(const Annotation& annotation) {
    if (!context_.GetSpanContext().IsSampled()) {
      return;
    }

    switch (annotation.type()) {
      // Annotations are expensive to create. We should only create it if the
      // call is being sampled by default.
      default:
        if (IsSampled()) {
          context_.AddSpanAnnotation(annotation.ToString());
        }
        break;
    }
}

//
// PythonOpenCensusServerCallTracerFactory
//

grpc_core::ServerCallTracer*
PythonOpenCensusServerCallTracerFactory::CreateNewServerCallTracer(
    grpc_core::Arena* arena, const grpc_core::ChannelArgs& channel_args) {
  // We don't use arena here to to ensure that memory is allocated and freed in
  // the same DLL in Windows.
  (void)arena;
  (void)channel_args;
  return new PythonOpenCensusServerCallTracer(additional_labels_, identifier_);
}

bool PythonOpenCensusServerCallTracerFactory::IsServerTraced(
    const grpc_core::ChannelArgs& args) {
  // Return true only if there is no server selector registered or if the server
  // selector returns true.
  return true;
}

PythonOpenCensusServerCallTracerFactory::PythonOpenCensusServerCallTracerFactory(
  const std::vector<Label>& additional_labels, const char* identifier)
    : additional_labels_(additional_labels), identifier_(identifier) {}

}  // namespace grpc_observability
