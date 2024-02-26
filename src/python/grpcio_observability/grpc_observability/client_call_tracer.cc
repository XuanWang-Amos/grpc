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

#include "client_call_tracer.h"

#include <stddef.h>

#include <algorithm>
#include <vector>
#include <typeinfo>

#include "absl/strings/str_cat.h"
#include "absl/time/clock.h"
#include "constants.h"
#include "observability_util.h"
#include "python_census_context.h"
#include "metadata_exchange.h"

#include <grpc/slice.h>

#include "src/core/lib/slice/slice.h"

namespace grpc_observability {

constexpr uint32_t PythonOpenCensusCallTracer::
    PythonOpenCensusCallAttemptTracer::kMaxTraceContextLen;
constexpr uint32_t
    PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::kMaxTagsLen;

//
// OpenCensusCallTracer
//

PythonOpenCensusCallTracer::PythonOpenCensusCallTracer(
    const char* method, const char* target, const char* trace_id, const char* parent_span_id,
    const char* identifier, const std::vector<Label>& additional_labels,
    bool add_csm_optional_labels, bool tracing_enabled)
    : method_(GetMethod(method)),
      target_(GetTarget(target)),
      tracing_enabled_(tracing_enabled),
      add_csm_optional_labels_(add_csm_optional_labels),
      // additional_labels_(additional_labels),
      labels_injector_(additional_labels),
      identifier_(identifier) {
  // std::cout << "[PythonOpenCensusCallTracer] Created with id: " << identifier_ << std::endl;
  GenerateClientContext(absl::StrCat("Sent.", method_),
                        absl::string_view(trace_id),
                        absl::string_view(parent_span_id), &context_);
}

void PythonOpenCensusCallTracer::GenerateContext() {}

void PythonOpenCensusCallTracer::RecordAnnotation(
    absl::string_view annotation) {
  if (!context_.GetSpanContext().IsSampled()) {
    return;
  }
  context_.AddSpanAnnotation(annotation);
}

void PythonOpenCensusCallTracer::RecordAnnotation(
    const Annotation& annotation) {
  if (!context_.GetSpanContext().IsSampled()) {
    return;
  }

  switch (annotation.type()) {
    // Annotations are expensive to create. We should only create it if the call
    // is being sampled by default.
    default:
      if (IsSampled()) {
        context_.AddSpanAnnotation(annotation.ToString());
      }
      break;
  }
}

PythonOpenCensusCallTracer::~PythonOpenCensusCallTracer() {
  if (PythonCensusStatsEnabled()) {
    context_.Labels().emplace_back(kClientMethod, std::string(method_));
    RecordIntMetric(kRpcClientRetriesPerCallMeasureName, retries_ - 1,
                    context_.Labels(), identifier_);  // exclude first attempt
    RecordIntMetric(kRpcClientTransparentRetriesPerCallMeasureName,
                    transparent_retries_, context_.Labels(), identifier_);
    RecordDoubleMetric(kRpcClientRetryDelayPerCallMeasureName,
                       ToDoubleSeconds(retry_delay_), context_.Labels(), identifier_);
  }

  if (tracing_enabled_) {
    context_.EndSpan();
    if (IsSampled()) {
      RecordSpan(context_.GetSpan().ToCensusData());
    }
  }
}

PythonCensusContext
PythonOpenCensusCallTracer::CreateCensusContextForCallAttempt() {
  auto context = PythonCensusContext(absl::StrCat("Attempt.", method_),
                                     &(context_.GetSpan()), context_.Labels());
  return context;
}

PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer*
PythonOpenCensusCallTracer::StartNewAttempt(bool is_transparent_retry) {
  uint64_t attempt_num;
  {
    grpc_core::MutexLock lock(&mu_);
    if (transparent_retries_ != 0 || retries_ != 0) {
      if (PythonCensusStatsEnabled() && num_active_rpcs_ == 0) {
        retry_delay_ += absl::Now() - time_at_last_attempt_end_;
      }
    }
    attempt_num = retries_;
    if (is_transparent_retry) {
      ++transparent_retries_;
    } else {
      ++retries_;
    }
    ++num_active_rpcs_;
  }
  context_.IncreaseChildSpanCount();
  return new PythonOpenCensusCallAttemptTracer(this, attempt_num,
                                               is_transparent_retry);
}

//
// PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer
//

PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    PythonOpenCensusCallAttemptTracer(PythonOpenCensusCallTracer* parent,
                                      uint64_t attempt_num,
                                      bool is_transparent_retry)
    : parent_(parent),
      context_(parent_->CreateCensusContextForCallAttempt()),
      start_time_(absl::Now()) {
  if (parent_->tracing_enabled_) {
    context_.AddSpanAttribute("previous-rpc-attempts",
                              absl::StrCat(attempt_num));
    context_.AddSpanAttribute("transparent-retry",
                              absl::StrCat(is_transparent_retry));
  }
  if (!PythonCensusStatsEnabled()) {
    return;
  }
  context_.Labels().emplace_back(kClientMethod, std::string(parent_->method_));
  context_.Labels().emplace_back(kClientTarget, std::string(parent_->target_));
  // std::cout << "parent_->additional_labels_ size: " << (parent_->additional_labels_).size() << std::endl;
  // for (auto& label : parent_->additional_labels_) {  
  //     std::cout << "parent_->additional_labels_: " << label.key << ", " << label.value << std::endl;
  // }
  // Get additional labels.
  // Skips here since we don't need any additional labels.
  // if (OpenTelemetryPluginState().client.attempt.started != nullptr) {
  //   std::array<std::pair<absl::string_view, absl::string_view>, 2>
  //       additional_labels = {
  //           {{OpenTelemetryMethodKey(), parent_->MethodForStats()},
  //            {OpenTelemetryTargetKey(), parent_->parent_->filtered_target()}}};
  //   // We might not have all the injected labels that we want at this point, so
  //   // avoid recording a subset of injected labels here.
  //   OpenTelemetryPluginState().client.attempt.started->Add(
  //       1, KeyValueIterable(/*injected_labels_from_plugin_options=*/{},
  //                           additional_labels,
  //                           /*active_plugin_options_view=*/nullptr,
  //                           /*optional_labels_span=*/{}, /*is_client=*/true));
  // }
  RecordIntMetric(kRpcClientStartedRpcsMeasureName, 1, context_.Labels(), parent_->identifier_);
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordSendInitialMetadata(grpc_metadata_batch* send_initial_metadata) {
  if (parent_->tracing_enabled_) {
    char tracing_buf[kMaxTraceContextLen];
    size_t tracing_len =
        TraceContextSerialize(context_, tracing_buf, kMaxTraceContextLen);
    if (tracing_len > 0) {
      send_initial_metadata->Set(
          grpc_core::GrpcTraceBinMetadata(),
          grpc_core::Slice::FromCopiedBuffer(tracing_buf, tracing_len));
    }
  }
  if (!PythonCensusStatsEnabled()) {
    return;
  }
  grpc_slice tags = grpc_empty_slice();
  size_t encoded_tags_len = StatsContextSerialize(kMaxTagsLen, &tags);
  if (encoded_tags_len > 0) {
    send_initial_metadata->Set(grpc_core::GrpcTagsBinMetadata(),
                               grpc_core::Slice(tags));
  }
  parent_->labels_injector_.ClientAddLabels(send_initial_metadata);
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordReceivedInitialMetadata(grpc_metadata_batch* recv_initial_metadata) {
  // Get labels from recv_initial_metadata and add to injected_labels_from_plugin_options_.
  // const std::unique_ptr<LabelsIterable>& plugin_option_injected_iterable = parent_->labels_injector_.GetLabels(recv_initial_metadata);
  // injected_labels_from_plugin_options_.push_back(parent_->labels_injector_.GetLabels(recv_initial_metadata));
  // for (const auto& plugin_option_injected_iterable : injected_labels_from_plugin_options_) {
  //   if (plugin_option_injected_iterable != nullptr) {
  //     plugin_option_injected_iterable->ResetIteratorPosition();
  //     while (const auto& pair = plugin_option_injected_iterable->Next()) {
  //       std::cout << "[CLIENT] labels from peer: " << pair->first << ": " << pair->second << std::endl;
  //     }
  //   }
  // }

  // injected_labels_ = parent_->labels_injector_.GetLabels(recv_initial_metadata);
  // auto peer_metadata = recv_initial_metadata->Take(grpc_core::XEnvoyPeerMetadata());
  // grpc_core::Slice remote_metadata = peer_metadata.has_value() ? *std::move(peer_metadata) : grpc_core::Slice();
  // if (remote_metadata.empty()) {
  //   std::cout << "[CLIENT] remote_metadata->empty() TRUE" << std::endl;
  // } else {
  //   std::string decoded_metadata;
  //   bool metadata_decoded =
  //       absl::Base64Unescape(remote_metadata.as_string_view(), &decoded_metadata);
  injected_labels_ = parent_->labels_injector_.GetLabels(recv_initial_metadata);

  for (const auto& label : injected_labels_) {
      std::cout << "[CLIENT] labels from peer: " << label.key << ": " << label.value << std::endl;
      context_.Labels().emplace_back(label);
  }
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordSendMessage(const grpc_core::SliceBuffer& /*send_message*/) {
  ++sent_message_count_;
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordReceivedMessage(const grpc_core::SliceBuffer& /*recv_message*/) {
  ++recv_message_count_;
}

std::shared_ptr<grpc_core::TcpTracerInterface> PythonOpenCensusCallTracer::
    PythonOpenCensusCallAttemptTracer::StartNewTcpTrace() {
  return nullptr;
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::AddOptionalLabels(
    OptionalLabelComponent component,
    std::shared_ptr<std::map<std::string, std::string>> optional_labels) {
  optional_labels_array_[static_cast<std::size_t>(component)] =
      std::move(optional_labels);
}


namespace {

// Returns 0 if no server stats are present in the metadata.
uint64_t GetElapsedTimeFromTrailingMetadata(const grpc_metadata_batch* b) {
  if (!PythonCensusStatsEnabled()) {
    return 0;
  }

  const grpc_core::Slice* grpc_server_stats_bin_ptr =
      b->get_pointer(grpc_core::GrpcServerStatsBinMetadata());
  if (grpc_server_stats_bin_ptr == nullptr) {
    return 0;
  }

  uint64_t elapsed_time = 0;
  ServerStatsDeserialize(
      reinterpret_cast<const char*>(grpc_server_stats_bin_ptr->data()),
      grpc_server_stats_bin_ptr->size(), &elapsed_time);
  return elapsed_time;
}

}  // namespace

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordReceivedTrailingMetadata(
        absl::Status status, grpc_metadata_batch* recv_trailing_metadata,
        const grpc_transport_stream_stats* transport_stream_stats) {
  if (!PythonCensusStatsEnabled()) {
    return;
  }
  auto status_code_ = status.code();
  uint64_t elapsed_time = 0;
  if (recv_trailing_metadata != nullptr) {
    elapsed_time = GetElapsedTimeFromTrailingMetadata(recv_trailing_metadata);
  }

  std::string final_status = absl::StatusCodeToString(status_code_);
  context_.Labels().emplace_back(kClientMethod, std::string(parent_->method_));
  context_.Labels().emplace_back(kClientTarget, std::string(parent_->target_));
  context_.Labels().emplace_back(kClientStatus, final_status);
  if (parent_->add_csm_optional_labels_) {
    parent_->labels_injector_.AddXdsOptionalLabels(/*is_client=*/true,
                                                   optional_labels_array_,
                                                   context_.Labels());
  }
  for (const auto& plugin_option_injected_iterable : injected_labels_from_plugin_options_) {
    if (plugin_option_injected_iterable != nullptr) {
      plugin_option_injected_iterable->ResetIteratorPosition();
      while (const auto& pair = plugin_option_injected_iterable->Next()) {
        // std::cout << "injected_labels_from_plugin_options_: " << pair->first << ": " << pair->second << std::endl;
        context_.Labels().emplace_back(std::string(pair->first), std::string(pair->second));
      }
    }
  }
  // std::cout << "[CALLTRACER] Adding data with identifier RecordReceivedTrailingMetadata: " << parent_->identifier_ << std::endl;
  RecordDoubleMetric(
      kRpcClientSentBytesPerRpcMeasureName,
      static_cast<double>(transport_stream_stats != nullptr
                              ? transport_stream_stats->outgoing.data_bytes
                              : 0),
      context_.Labels(), parent_->identifier_);
  RecordDoubleMetric(
      kRpcClientReceivedBytesPerRpcMeasureName,
      static_cast<double>(transport_stream_stats != nullptr
                              ? transport_stream_stats->incoming.data_bytes
                              : 0),
      context_.Labels(), parent_->identifier_);
  RecordDoubleMetric(kRpcClientServerLatencyMeasureName,
                     absl::ToDoubleSeconds(absl::Nanoseconds(elapsed_time)),
                     context_.Labels(), parent_->identifier_);
  RecordDoubleMetric(kRpcClientRoundtripLatencyMeasureName,
                     absl::ToDoubleSeconds(absl::Now() - start_time_),
                     context_.Labels(), parent_->identifier_);
  RecordIntMetric(kRpcClientCompletedRpcMeasureName, 1, context_.Labels(), parent_->identifier_);
  // std::array<std::pair<absl::string_view, absl::string_view>, 3>
  //     additional_labels = {
  //         {{OpenTelemetryMethodKey(), parent_->MethodForStats()},
  //          {OpenTelemetryTargetKey(), parent_->parent_->filtered_target()},
  //          {OpenTelemetryStatusKey(),
  //           grpc_status_code_to_string(
  //               static_cast<grpc_status_code>(status.code()))}}};
  // KeyValueIterable labels(injected_labels_from_plugin_options_,
  //                         additional_labels,
  //                         &parent_->parent_->active_plugin_options_view(),
  //                         optional_labels_array_, /*is_client=*/true);
  // if (OpenTelemetryPluginState().client.attempt.duration != nullptr) {
  //   OpenTelemetryPluginState().client.attempt.duration->Record(
  //       absl::ToDoubleSeconds(absl::Now() - start_time_), labels,
  //       opentelemetry::context::Context{});
  // }
  // if (OpenTelemetryPluginState()
  //         .client.attempt.sent_total_compressed_message_size != nullptr) {
  //   OpenTelemetryPluginState()
  //       .client.attempt.sent_total_compressed_message_size->Record(
  //           transport_stream_stats != nullptr
  //               ? transport_stream_stats->outgoing.data_bytes
  //               : 0,
  //           labels, opentelemetry::context::Context{});
  // }
  // if (OpenTelemetryPluginState()
  //         .client.attempt.rcvd_total_compressed_message_size != nullptr) {
  //   OpenTelemetryPluginState()
  //       .client.attempt.rcvd_total_compressed_message_size->Record(
  //           transport_stream_stats != nullptr
  //               ? transport_stream_stats->incoming.data_bytes
  //               : 0,
  //           labels, opentelemetry::context::Context{});
  // }
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordCancel(absl::Status /*cancel_error*/) {}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::RecordEnd(
    const gpr_timespec& /*latency*/) {
  if (PythonCensusStatsEnabled()) {
    context_.Labels().emplace_back(kClientMethod,
                                   std::string(parent_->method_));
    context_.Labels().emplace_back(kClientStatus,
                                   StatusCodeToString(status_code_));
    // std::cout << "[CALLTRACER] Adding data with identifier RecordEnd: " << parent_->identifier_ << std::endl;
    RecordIntMetric(kRpcClientSentMessagesPerRpcMeasureName,
                    sent_message_count_, context_.Labels(), parent_->identifier_);
    RecordIntMetric(kRpcClientReceivedMessagesPerRpcMeasureName,
                    recv_message_count_, context_.Labels(), parent_->identifier_);

    grpc_core::MutexLock lock(&parent_->mu_);
    if (--parent_->num_active_rpcs_ == 0) {
      parent_->time_at_last_attempt_end_ = absl::Now();
    }
  }

  if (parent_->tracing_enabled_) {
    if (status_code_ != absl::StatusCode::kOk) {
      context_.GetSpan().SetStatus(StatusCodeToString(status_code_));
    }
    context_.EndSpan();
    if (IsSampled()) {
      RecordSpan(context_.GetSpan().ToCensusData());
    }
  }

  // After RecordEnd, Core will make no further usage of this CallAttemptTracer,
  // so we are free it here.
  delete this;
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordAnnotation(absl::string_view annotation) {
  if (!context_.GetSpanContext().IsSampled()) {
    return;
  }
  context_.AddSpanAnnotation(annotation);
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordAnnotation(const Annotation& annotation) {
  if (!context_.GetSpanContext().IsSampled()) {
    return;
  }

  switch (annotation.type()) {
    // Annotations are expensive to create. We should only create it if the call
    // is being sampled by default.
    default:
      if (IsSampled()) {
        context_.AddSpanAnnotation(annotation.ToString());
      }
      break;
  }
}

}  // namespace grpc_observability
