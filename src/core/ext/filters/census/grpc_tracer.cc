//
//
// Copyright 2015 gRPC authors.
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

#include <grpc/support/port_platform.h>
#include <grpc/grpc.h>
#include <stdio.h>
#include <iostream>

#include "src/core/lib/channel/context.h"
#include "src/core/lib/channel/call_tracer.h"
#include "src/core/lib/debug/trace.h"
#include "src/core/lib/surface/api_trace.h"
#include "src/core/lib/surface/call.h"

void grpc_call_set_call_tracer(grpc_call* call, const void* call_tracer) {
  setbuf(stdout, NULL);
  GRPC_API_TRACE("grpc_call_set_call_tracer(call=%p, call_tracer=%p)", 2,
                 (call, call_tracer));
  if (call_tracer != nullptr) {
    std::cout << "  call_tracer != nullptr, call_tracer= " << call_tracer << std::endl;

    grpc_core::ClientCallTracer* ptr = (grpc_core::ClientCallTracer*)call_tracer;

    std::cout << "  Setting call tracer to call_context_[GRPC_CONTEXT_CALL_TRACER_ANNOTATION_INTERFACE]: " << std::endl;
    grpc_call_context_set(call, GRPC_CONTEXT_CALL_TRACER_ANNOTATION_INTERFACE, ptr, nullptr);
  }
}

void* grpc_call_get_call_tracer(grpc_call* call) {
  GRPC_API_TRACE("grpc_call_get_call_tracer(grpc_call=%p)", 1,
                 (call));
  std::cout << "GRPC_API_TRACE[grpc_call_get_call_tracer]:" << std::endl;

  // OR GRPC_CONTEXT_CALL_TRACER
  void* call_tracer = grpc_call_context_get(call, GRPC_CONTEXT_CALL_TRACER_ANNOTATION_INTERFACE);
  std::cout << "   call_tracer=" << call_tracer << std::endl;

  return call_tracer;
}

void grpc_register_server_call_tracer_factory(const void* call_tracer_factory) {
  setbuf(stdout, NULL);
  GRPC_API_TRACE("grpc_register_server_call_tracer_factory(call_tracer_factory=%p)", 1,
                 (call_tracer_factory));
  std::cout << "GRPC_API_TRACE[grpc_register_server_call_tracer_factory]:" << std::endl;

  if (call_tracer_factory != nullptr) {
    std::cout << "  call_tracer_factory != nullptr, call_tracer_factory= " << call_tracer_factory << std::endl;

    grpc_core::ServerCallTracerFactory* ptr = (grpc_core::ServerCallTracerFactory*)call_tracer_factory;
    grpc_core::ServerCallTracerFactory::RegisterGlobal(ptr);
  }
}
