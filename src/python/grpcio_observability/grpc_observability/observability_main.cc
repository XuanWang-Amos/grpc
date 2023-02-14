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

#include "observability_main.h"
#include "server_call_tracer.h"
#include "client_call_tracer.h"

#include "absl/strings/escaping.h"
#include "absl/strings/string_view.h"

#include <limits.h>

#include <atomic>

namespace grpc_observability {

std::queue<CensusData> kSensusDataBuffer;
std::mutex kSensusDataBufferMutex;
std::condition_variable SensusDataBufferCV;

void RecordMetricSensusData(Measurement measurement, std::vector<Label> labels) {
  // std::cout << "------ Record Start ------ " << std::endl;
  // std::cout << "measurement.name: " << measurement.name << std::endl;
  // std::cout << "measurement.type: " << measurement.type << std::endl;
  // std::cout << "measurement.value.value_double: " << measurement.value.value_double << std::endl;
  // std::cout << "measurement.value.value_int: " << measurement.value.value_int << std::endl;
  // std::cout << "&measurement: " << &measurement << std::endl;
  // std::cout << "------ Record End ------ " << std::endl;
  CensusData data = CensusData(measurement, labels);
  AddCensusDataToBuffer(data);
}

void RecordSpanSensusData(SpanSensusData spanSensusData) {
  CensusData data = CensusData(spanSensusData);
  std::cout << " ________Record SPAN: " << spanSensusData.name << " with id: " << spanSensusData.span_id << std::endl;
  AddCensusDataToBuffer(data);
}

Measurement CreateIntMeasurement(MetricsName name, int64_t value) {
  Measurement single_measurement;
  single_measurement.type = kMeasurementInt;
  single_measurement.name = name;
  single_measurement.value.value_int = value;
  return single_measurement;
}

Measurement CreateDoubleMeasurement(MetricsName name, double value) {
  Measurement single_measurement;
  single_measurement.type = kMeasurementDouble;
  single_measurement.name = name;
  single_measurement.value.value_double = value;
  return single_measurement;
}

//
// Others
//

void gcpObservabilityInit() {
    setbuf(stdout, nullptr);
    std::cout << "Calling grpc::experimental::GcpObservabilityInit()"; std::cout << std::endl;
}

void* CreateClientCallTracer(char* method, char* trace_id, char* parent_span_id) {
    std::cout << "Inside grpc_o11y.CreateClientCallTracer" << std::endl;
    std::cout << "  ---->>> method: "  << method  << " string(method):" << std::string(method) << std::endl;
    std::cout << "  ---->>> trace_id: "  << trace_id << std::endl;
    std::cout << "  ---->>> parent_span_id: " << parent_span_id << std::endl;
    std::cout << "  ---->>> tracing_enabled: " << (OpenCensusTracingEnabled() ? "True" : "False") << std::endl;
    void* client_call_tracer = new PythonOpenCensusCallTracer(method, trace_id, parent_span_id, OpenCensusTracingEnabled());

    std::cout << "created client call tracer with address in void* format:" << client_call_tracer << std::endl;
    return client_call_tracer;
}

void* CreateServerCallTracerFactory() {
    std::cout << "Inside grpc_o11y.CreateServerCallTracerFactory" << std::endl;
    void* server_call_tracer_factory = new PythonOpenCensusServerCallTracerFactory();

    std::cout << "created server tracer factory with address in void* format:" << server_call_tracer_factory << std::endl;
    return server_call_tracer_factory;
}

void AwaitNextBatch(int timeout_ms) {
  std::unique_lock<std::mutex> lk(kSensusDataBufferMutex);
  auto now = std::chrono::system_clock::now();
  auto status = SensusDataBufferCV.wait_until(lk, now + std::chrono::milliseconds(timeout_ms));
  if (status == std::cv_status::no_timeout) {
    std::cout << "> Exporting Thread: Waiting Finished no_timeout" << std::endl;
  } else {
    std::cout << "> Exporting Thread: Waiting Finished timeout" << std::endl;
  }
}

void LockSensusDataBuffer() {
  kSensusDataBufferMutex.lock();
  // std::cout << "> Exporting Thread: >>>>>>>> LOCKED <<<<<<<<<< at " << absl::Now() << std::endl;
}

void UnlockSensusDataBuffer() {
  // std::cout << "> Exporting Thread: >>>>>>>> UN-LOCKED <<<<<<<<<< at " << absl::Now() << std::endl;
  kSensusDataBufferMutex.unlock();
}

void AddCensusDataToBuffer(CensusData data) {
  // std::cout << ">>>>>>>> Trying to get LOCK before adding to queue <<<<<<<<<<" << std::endl;
  std::unique_lock<std::mutex> lk(kSensusDataBufferMutex);
  // std::cout << ">>>>>>>> LOCKED QUEUE Adding <<<<<<<<<<" << std::endl;
  kSensusDataBuffer.push(data);
  if (kSensusDataBuffer.size() >= 2) {
      SensusDataBufferCV.notify_all();
  }
  // std::cout << ">>>>>>>> UN-LOCKING QUEUE Adding <<<<<<<<<<" << std::endl;
}

absl::string_view StatusCodeToString(grpc_status_code code) {
  switch (code) {
    case GRPC_STATUS_OK:
      return "OK";
    case GRPC_STATUS_CANCELLED:
      return "CANCELLED";
    case GRPC_STATUS_UNKNOWN:
      return "UNKNOWN";
    case GRPC_STATUS_INVALID_ARGUMENT:
      return "INVALID_ARGUMENT";
    case GRPC_STATUS_DEADLINE_EXCEEDED:
      return "DEADLINE_EXCEEDED";
    case GRPC_STATUS_NOT_FOUND:
      return "NOT_FOUND";
    case GRPC_STATUS_ALREADY_EXISTS:
      return "ALREADY_EXISTS";
    case GRPC_STATUS_PERMISSION_DENIED:
      return "PERMISSION_DENIED";
    case GRPC_STATUS_UNAUTHENTICATED:
      return "UNAUTHENTICATED";
    case GRPC_STATUS_RESOURCE_EXHAUSTED:
      return "RESOURCE_EXHAUSTED";
    case GRPC_STATUS_FAILED_PRECONDITION:
      return "FAILED_PRECONDITION";
    case GRPC_STATUS_ABORTED:
      return "ABORTED";
    case GRPC_STATUS_OUT_OF_RANGE:
      return "OUT_OF_RANGE";
    case GRPC_STATUS_UNIMPLEMENTED:
      return "UNIMPLEMENTED";
    case GRPC_STATUS_INTERNAL:
      return "INTERNAL";
    case GRPC_STATUS_UNAVAILABLE:
      return "UNAVAILABLE";
    case GRPC_STATUS_DATA_LOSS:
      return "DATA_LOSS";
    default:
      // gRPC wants users of this enum to include a default branch so that
      // adding values is not a breaking change.
      return "UNKNOWN_STATUS";
  }
}

GcpObservabilityConfig ReadObservabilityConfig() {
  auto config = grpc::internal::GcpObservabilityConfig::ReadFromEnv();

  if (!config.ok()) {
    std::cout << ">>>>> !config.ok <<<<< " << std::endl;
    return GcpObservabilityConfig();
  }
  if (!config->cloud_trace.has_value() &&
      !config->cloud_monitoring.has_value() &&
      !config->cloud_logging.has_value()) {
    std::cout << ">>>>> config no value for all <<<<< " << std::endl;
    return GcpObservabilityConfig();
  }

  if (!config->cloud_trace.has_value()) {
    // Disable OpenCensus tracing
    std::cout << "------ Disable OpenCensus tracing ------ " << std::endl;
    EnableOpenCensusTracing(false);
  }
  if (!config->cloud_monitoring.has_value()) {
    // Disable OpenCensus stats
    std::cout << "------ Disable OpenCensus stats ------ " << std::endl;
    EnableOpenCensusStats(false);
  }

  std::vector<Label> labels;
  std::string project_id = config->project_id;
  CloudMonitoring cloud_monitoring_config = CloudMonitoring();
  CloudTrace cloud_trace_config = CloudTrace();
  CloudLogging cloud_logging_config = CloudLogging();

  if (config->cloud_trace.has_value() || config->cloud_monitoring.has_value()) {
    labels.reserve(config->labels.size());
    // Insert in user defined labels from the GCP Observability config.
    for (const auto& label : config->labels) {
      labels.push_back(Label{label.first, label.second});
    }

    if (config->cloud_trace.has_value()) {
      double sampleRate = config->cloud_trace->sampling_rate;
      cloud_trace_config = CloudTrace(sampleRate);
    }
    if (config->cloud_monitoring.has_value()) {
      cloud_monitoring_config = CloudMonitoring();
    }
  }

  // Clound logging
  if (config->cloud_logging.has_value()) {
    // TODO(xuanwn): Read cloud logging config
  }

  return GcpObservabilityConfig(cloud_monitoring_config, cloud_trace_config, cloud_logging_config, project_id, labels);
}

}  // namespace grpc_observability
