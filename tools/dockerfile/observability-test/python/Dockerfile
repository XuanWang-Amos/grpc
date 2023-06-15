# Copyright 2022 gRPC authors.
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


#
# Stage 1: Build the interop test client and server
#

FROM debian:11 as build

RUN apt-get update && apt-get install -y python3 python3-dev python3-pip curl git
# RUN ln -s $(which python3) /usr/bin/python
# RUN python3 -m pip install --upgrade opencensus==0.10.0 opencensus-ext-stackdriver==0.8.0

WORKDIR /grpc
COPY . .

# /grpc/tools/bazel build test/cpp/interop:observability_interop_test
RUN git submodule update --init --recursive && \
  /grpc/tools/bazel build src/python/grpcio_tests/tests/interop:observability_client && \
  /grpc/tools/bazel build src/python/grpcio_tests/tests/interop:observability_server

#
# Stage 2:
#
# - Copy only the necessary files to reduce Docker image size.
# - Have an ENTRYPOINT script which will launch the interop test client or server
#   with the given parameters.
#

FROM debian:11

# ENV GRPC_TRACE environment_autodetect
ENV GRPC_VERBOSITY debug


WORKDIR /usr/share/grpc
COPY --from=build /grpc/etc/roots.pem .


WORKDIR /grpc/bazel-bin/src/python/grpcio_tests/tests/interop
COPY --from=build /grpc/bazel-bin/src/python/grpcio_tests/tests/interop/observability_server .
COPY --from=build /grpc/bazel-bin/src/python/grpcio_tests/tests/interop/observability_client .

WORKDIR /grpc/tools/dockerfile/observability-test/python
COPY --from=build /grpc/tools/dockerfile/observability-test/python/run.sh .

ENTRYPOINT ["/grpc/tools/dockerfile/observability-test/python/run.sh"]
