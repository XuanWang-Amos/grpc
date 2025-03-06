#! /bin/bash
# Copyright 2025 gRPC authors.
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


set -e

GRPC_ROOT=$(realpath "$(dirname "$0")/../..")

# Source and destination directories (base paths).
SRC_BASE="$GRPC_ROOT/src/proto/grpc"
DST_BASE="$GRPC_ROOT/src/python"

copy_proto() {
  local proto_name="$1"
  local src_subdir="$2"
  local dst_subdir="$3"

  local src_file="$SRC_BASE/$src_subdir/$proto_name.proto"
  local dst_file="$DST_BASE/$dst_subdir/$proto_name.proto"

  cp "$src_file" "$dst_file"
  echo "Copied: $src_file -> $dst_file"
}

# copy_proto proto_name src_subdir dst_subdir
copy_proto "channelz" "channelz" "grpcio_channelz/grpc_channelz/v1"
copy_proto "health" "health/v1" "grpcio_health_checking/grpc_health/v1"
copy_proto "reflection" "reflection/v1alpha" "grpcio_reflection/grpc_reflection/v1alpha"

echo "Proto files copied successfully."
