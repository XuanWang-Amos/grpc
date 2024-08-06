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

#include "absl/strings/str_cat.h"
#include "absl/time/clock.h"
#include "constants.h"
#include "metadata_exchange.h"
#include "observability_util.h"
#include "python_observability_context.h"

#include <grpc/slice.h>

#include "src/core/lib/experiments/experiments.h"
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
    const char* method, const char* target, const char* trace_id,
    const char* parent_span_id, const char* identifier,
    const std::vector<Label>& exchange_labels, bool tracing_enabled,
    bool add_csm_optional_labels, bool registered_method)
    : method_(GetMethod(method)),
      target_(GetTarget(target)),
      tracing_enabled_(tracing_enabled),
      add_csm_optional_labels_(add_csm_optional_labels),
      labels_injector_(exchange_labels),
      identifier_(identifier),
      registered_method_(registered_method) {
  LOG(INFO) << "[xuanwn_testing] Create PythonOpenCensusCallTracer";
  GenerateClientContext(absl::StrCat("Sent.", method_),
                        absl::string_view(trace_id),
                        absl::string_view(parent_span_id), &context_);
  LOG(INFO) << "[xuanwn_testing] Create PythonOpenCensusCallTracer end";
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
  LOG(INFO) << "[xuanwn_testing] calling ~PythonOpenCensusCallTracer for "
            << this;
  if (PythonCensusStatsEnabled()) {
    context_.Labels().emplace_back(kClientMethod, method_);
    RecordIntMetric(kRpcClientRetriesPerCallMeasureName, retries_ - 1,
                    context_.Labels(), identifier_, registered_method_,
                    /*include_exchange_labels=*/true);  // exclude first attempt
    RecordIntMetric(kRpcClientTransparentRetriesPerCallMeasureName,
                    transparent_retries_, context_.Labels(), identifier_,
                    registered_method_, /*include_exchange_labels=*/true);
    RecordDoubleMetric(kRpcClientRetryDelayPerCallMeasureName,
                       ToDoubleSeconds(retry_delay_), context_.Labels(),
                       identifier_, registered_method_,
                       /*include_exchange_labels=*/true);
  }

  if (tracing_enabled_) {
    context_.EndSpan();
    if (IsSampled()) {
      RecordSpan(context_.GetSpan().ToCensusData());
    }
  }
  LOG(INFO) << "[xuanwn_testing] ~PythonOpenCensusCallTracer calling end";
}

PythonCensusContext
PythonOpenCensusCallTracer::CreateCensusContextForCallAttempt() {
  LOG(INFO) << "[xuanwn_testing] calling CreateCensusContextForCallAttempt";
  auto context = PythonCensusContext(absl::StrCat("Attempt.", method_),
                                     &(context_.GetSpan()), context_.Labels());
  return context;
}

PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer*
PythonOpenCensusCallTracer::StartNewAttempt(bool is_transparent_retry) {
  LOG(INFO) << "[xuanwn_testing] calling StartNewAttempt";
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
  LOG(INFO) << "[xuanwn_testing] calling PythonOpenCensusCallAttemptTracer";
  if (parent_->tracing_enabled_) {
    context_.AddSpanAttribute("previous-rpc-attempts",
                              absl::StrCat(attempt_num));
    context_.AddSpanAttribute("transparent-retry",
                              absl::StrCat(is_transparent_retry));
  }
  if (!PythonCensusStatsEnabled()) {
    return;
  }
  context_.Labels().emplace_back(kClientMethod, parent_->method_);
  context_.Labels().emplace_back(kClientTarget, parent_->target_);
  RecordIntMetric(kRpcClientStartedRpcsMeasureName, 1, context_.Labels(),
                  parent_->identifier_, parent_->registered_method_,
                  /*include_exchange_labels=*/false);
  LOG(INFO) << "[xuanwn_testing] PythonOpenCensusCallAttemptTracer end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordSendInitialMetadata(grpc_metadata_batch* send_initial_metadata) {
  LOG(INFO) << "[xuanwn_testing] calling RecordSendInitialMetadata";
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
  LOG(INFO) << "[xuanwn_testing] calling AddExchangeLabelsToMetadata";
  parent_->labels_injector_.AddExchangeLabelsToMetadata(send_initial_metadata);
  LOG(INFO) << "[xuanwn_testing] AddExchangeLabelsToMetadata end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordReceivedInitialMetadata(grpc_metadata_batch* recv_initial_metadata) {
  LOG(INFO) << "[xuanwn_testing] calling RecordReceivedInitialMetadata";
  if (recv_initial_metadata != nullptr &&
      recv_initial_metadata->get(grpc_core::GrpcTrailersOnly())
          .value_or(false)) {
    is_trailers_only_ = true;
    return;
  }
  LOG(INFO) << "[xuanwn_testing] calling GetExchangeLabels";
  labels_from_peer_ =
      parent_->labels_injector_.GetExchangeLabels(recv_initial_metadata);
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordSendMessage(const grpc_core::SliceBuffer& /*send_message*/) {
  LOG(INFO) << "[xuanwn_testing] calling RecordSendMessage";
  ++sent_message_count_;
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordReceivedMessage(const grpc_core::SliceBuffer& /*recv_message*/) {
  LOG(INFO) << "[xuanwn_testing] calling RecordReceivedMessage";
  ++recv_message_count_;
  LOG(INFO) << "[xuanwn_testing] calling end";
}

std::shared_ptr<grpc_core::TcpTracerInterface> PythonOpenCensusCallTracer::
    PythonOpenCensusCallAttemptTracer::StartNewTcpTrace() {
  LOG(INFO) << "[xuanwn_testing] calling StartNewTcpTrace";
  return nullptr;
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    SetOptionalLabel(OptionalLabelKey key,
                     grpc_core::RefCountedStringValue value) {
  LOG(INFO) << "[xuanwn_testing] calling SetOptionalLabel";
  optional_labels_array_[static_cast<size_t>(key)] = std::move(value);
  LOG(INFO) << "[xuanwn_testing] calling end";
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
  LOG(INFO) << "[xuanwn_testing] calling RecordReceivedTrailingMetadata";
  if (!PythonCensusStatsEnabled()) {
    return;
  }
  if (is_trailers_only_) {
    labels_from_peer_ =
        parent_->labels_injector_.GetExchangeLabels(recv_trailing_metadata);
  }
  auto status_code_ = status.code();
  uint64_t elapsed_time = 0;
  if (recv_trailing_metadata != nullptr) {
    elapsed_time = GetElapsedTimeFromTrailingMetadata(recv_trailing_metadata);
  }

  std::string final_status = absl::StatusCodeToString(status_code_);
  context_.Labels().emplace_back(kClientMethod, parent_->method_);
  context_.Labels().emplace_back(kClientTarget, parent_->target_);
  context_.Labels().emplace_back(kClientStatus, final_status);
  if (parent_->add_csm_optional_labels_) {
    parent_->labels_injector_.AddXdsOptionalLabels(
        /*is_client=*/true, optional_labels_array_, context_.Labels());
  }
  for (const auto& label : labels_from_peer_) {
    context_.Labels().emplace_back(label);
  }
  uint64_t incoming_bytes = 0;
  uint64_t outgoing_bytes = 0;
  if (grpc_core::IsCallTracerInTransportEnabled()) {
    incoming_bytes = incoming_bytes_.load();
    outgoing_bytes = outgoing_bytes_.load();
  } else if (transport_stream_stats != nullptr) {
    incoming_bytes = transport_stream_stats->incoming.data_bytes;
    outgoing_bytes = transport_stream_stats->outgoing.data_bytes;
  }
  LOG(INFO) << "[xuanwn_testing] calling RecordDoubleMetric";
  RecordDoubleMetric(kRpcClientSentBytesPerRpcMeasureName,
                     static_cast<double>(outgoing_bytes), context_.Labels(),
                     parent_->identifier_, parent_->registered_method_,
                     /*include_exchange_labels=*/true);
  RecordDoubleMetric(kRpcClientReceivedBytesPerRpcMeasureName,
                     static_cast<double>(incoming_bytes), context_.Labels(),
                     parent_->identifier_, parent_->registered_method_,
                     /*include_exchange_labels=*/true);
  RecordDoubleMetric(kRpcClientServerLatencyMeasureName,
                     absl::ToDoubleSeconds(absl::Nanoseconds(elapsed_time)),
                     context_.Labels(), parent_->identifier_,
                     parent_->registered_method_,
                     /*include_exchange_labels=*/true);
  RecordDoubleMetric(kRpcClientRoundtripLatencyMeasureName,
                     absl::ToDoubleSeconds(absl::Now() - start_time_),
                     context_.Labels(), parent_->identifier_,
                     parent_->registered_method_,
                     /*include_exchange_labels=*/true);
  RecordIntMetric(kRpcClientCompletedRpcMeasureName, 1, context_.Labels(),
                  parent_->identifier_, parent_->registered_method_,
                  /*include_exchange_labels=*/true);
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordIncomingBytes(const TransportByteSize& transport_byte_size) {
  LOG(INFO) << "[xuanwn_testing] calling RecordIncomingBytes";
  incoming_bytes_.fetch_add(transport_byte_size.data_bytes);
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordOutgoingBytes(const TransportByteSize& transport_byte_size) {
  LOG(INFO) << "[xuanwn_testing] calling RecordOutgoingBytes";
  outgoing_bytes_.fetch_add(transport_byte_size.data_bytes);
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordCancel(absl::Status /*cancel_error*/) {}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::RecordEnd(
    const gpr_timespec& /*latency*/) {
  LOG(INFO) << "[xuanwn_testing] calling RecordEnd with parent: " << parent_;
  if (PythonCensusStatsEnabled()) {
    LOG(INFO) << "[xuanwn_testing] calling parent_->method_";
    context_.Labels().emplace_back(kClientMethod, parent_->method_);
    LOG(INFO) << "[xuanwn_testing] calling StatusCodeToString";
    context_.Labels().emplace_back(kClientStatus,
                                   StatusCodeToString(status_code_));
    LOG(INFO)
        << "[xuanwn_testing] calling kRpcClientSentMessagesPerRpcMeasureName";
    RecordIntMetric(kRpcClientSentMessagesPerRpcMeasureName,
                    sent_message_count_, context_.Labels(),
                    parent_->identifier_, parent_->registered_method_,
                    /*include_exchange_labels=*/true);
    LOG(INFO) << "[xuanwn_testing] calling "
                 "kRpcClientReceivedMessagesPerRpcMeasureName";
    RecordIntMetric(kRpcClientReceivedMessagesPerRpcMeasureName,
                    recv_message_count_, context_.Labels(),
                    parent_->identifier_, parent_->registered_method_,
                    /*include_exchange_labels=*/true);
    LOG(INFO) << "[xuanwn_testing] calling lock";
    grpc_core::MutexLock lock(&parent_->mu_);
    LOG(INFO) << "[xuanwn_testing] calling --parent_";
    if (--parent_->num_active_rpcs_ == 0) {
      LOG(INFO)
          << "[xuanwn_testing] calling parent_->time_at_last_attempt_end_";
      parent_->time_at_last_attempt_end_ = absl::Now();
    }
  }
  LOG(INFO) << "[xuanwn_testing] calling parent_->tracing_enabled_";
  if (parent_->tracing_enabled_) {
    if (status_code_ != absl::StatusCode::kOk) {
      LOG(INFO) << "[xuanwn_testing] calling StatusCodeToString(status_code_)";
      context_.GetSpan().SetStatus(StatusCodeToString(status_code_));
    }
    LOG(INFO) << "[xuanwn_testing] calling context_.EndSpan()";
    context_.EndSpan();
    if (IsSampled()) {
      RecordSpan(context_.GetSpan().ToCensusData());
    }
  }
  LOG(INFO) << "[xuanwn_testing] calling delete";
  // After RecordEnd, Core will make no further usage of this CallAttemptTracer,
  // so we are free it here.
  delete this;
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordAnnotation(absl::string_view annotation) {
  LOG(INFO) << "[xuanwn_testing] calling RecordAnnotation";
  if (!context_.GetSpanContext().IsSampled()) {
    return;
  }
  context_.AddSpanAnnotation(annotation);
  LOG(INFO) << "[xuanwn_testing] calling end";
}

void PythonOpenCensusCallTracer::PythonOpenCensusCallAttemptTracer::
    RecordAnnotation(const Annotation& annotation) {
  LOG(INFO) << "[xuanwn_testing] calling RecordAnnotation";
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
  LOG(INFO) << "[xuanwn_testing] calling end";
}

}  // namespace grpc_observability
