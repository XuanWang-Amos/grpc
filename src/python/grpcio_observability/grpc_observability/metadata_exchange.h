//
//
// Copyright 2024 gRPC authors.
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
//
//

#ifndef GRPC_PYTHON_OBSERVABILITY_METADATA_EXCHANGE_H
#define GRPC_PYTHON_OBSERVABILITY_METADATA_EXCHANGE_H

#include <stddef.h>
#include <stdint.h>

#include <bitset>
#include <memory>
#include <string>
#include <utility>

// #include "absl/container/flat_hash_set.h"
// #include "absl/functional/any_invocable.h"
#include "absl/strings/string_view.h"
#include "absl/types/optional.h"

#include "python_census_context.h"
#include "src/core/lib/transport/metadata_batch.h"

namespace grpc_observability {

// An iterable container interface that can be used as a return type for the
// OpenTelemetry plugin's label injector.
class LabelsIterable {
 public:
  virtual ~LabelsIterable() = default;

  // Returns the key-value label at the current position or absl::nullopt if the
  // iterator has reached the end.
  virtual absl::optional<std::pair<absl::string_view, absl::string_view>>
  Next() = 0;

  virtual size_t Size() const = 0;

  // Resets position of iterator to the start.
  virtual void ResetIteratorPosition() = 0;
};


// An interface that allows you to add additional labels on the calls traced
// through the OpenTelemetry plugin.
class LabelsInjector {
 public:
  virtual ~LabelsInjector() {}
  // Read the incoming initial metadata to get the set of labels to be added to
  // metrics.
  virtual std::unique_ptr<LabelsIterable> GetLabels(
      grpc_metadata_batch* incoming_initial_metadata) const = 0;

  // Modify the outgoing initial metadata with metadata information to be sent
  // to the peer. On the server side, \a labels_from_incoming_metadata returned
  // from `GetLabels` should be provided as input here. On the client side, this
  // should be nullptr.
  virtual void AddLabels(
      grpc_metadata_batch* outgoing_initial_metadata,
      LabelsIterable* labels_from_incoming_metadata) const = 0;

//   // Adds optional labels to the traced calls. Each entry in the span
//   // corresponds to the CallAttemptTracer::OptionalLabelComponent enum. Returns
//   // false when callback returns false.
//   virtual bool AddOptionalLabels(
//       bool is_client,
//       absl::Span<const std::shared_ptr<std::map<std::string, std::string>>>
//           optional_labels_span,
//       opentelemetry::nostd::function_ref<
//           bool(opentelemetry::nostd::string_view,
//                opentelemetry::common::AttributeValue)>
//           callback) const = 0;

//   // Gets the actual size of the optional labels that the Plugin is going to
//   // produce through the AddOptionalLabels method.
//   virtual size_t GetOptionalLabelsSize(
//       bool is_client,
//       absl::Span<const std::shared_ptr<std::map<std::string, std::string>>>
//           optional_labels_span) const = 0;
};

class PythonLabelsInjector : public LabelsInjector {
 public:
  explicit PythonLabelsInjector(const std::vector<Label>& additional_labels);

  // Read the incoming initial metadata to get the set of labels to be added to
  // metrics.
  std::unique_ptr<LabelsIterable> GetLabels(
      grpc_metadata_batch* incoming_initial_metadata) const override;

  // Modify the outgoing initial metadata with metadata information to be sent
  // to the peer.
  void AddLabels(grpc_metadata_batch* outgoing_initial_metadata,
                 LabelsIterable* labels_from_incoming_metadata) const override;

  // Add optional xds labels to the traced calls.
  void AddXdsOptionalLabels(
      bool is_client,
      absl::Span<const std::shared_ptr<std::map<std::string, std::string>>>
          optional_labels_span,
      std::vector<Label>& labels);

  // Gets the size of the actual optional labels.
//   size_t GetOptionalLabelsSize(
//       bool is_client,
//       absl::Span<const std::shared_ptr<std::map<std::string, std::string>>>
//           optional_labels_span) const override;

 private:
  std::vector<std::pair<absl::string_view, std::string>> local_labels_;
  grpc_core::Slice serialized_labels_to_send_;
};

}  // namespace grpc_observability

#endif  // GRPC_PYTHON_OBSERVABILITY_CONSTANTS_H
