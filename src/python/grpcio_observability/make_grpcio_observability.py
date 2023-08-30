#!/usr/bin/env python3

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

from __future__ import print_function

import errno
import os
import os.path
import pprint
import shutil
import subprocess
import sys
import traceback

# the template for the content of observability_lib_deps.py
DEPS_FILE_CONTENT = """
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

# AUTO-GENERATED BY make_grpcio_observability.py!
CC_FILES={cc_files}

CC_INCLUDES={cc_includes}

{commit_hash_expr}
"""

# expose commit hash suffix and prefix for check_grpcio_tools.py
COMMIT_HASH_PREFIX = 'PROTOBUF_SUBMODULE_VERSION="'
COMMIT_HASH_SUFFIX = '"'

EXTERNAL_LINKS = [
    ('@com_google_absl//', 'third_party/abseil-cpp/'),
    ("@com_google_protobuf//", "third_party/protobuf/"),
    ('@upb//:', 'third_party/upb/'),
    ('@utf8_range//:', 'third_party/utf8_range/'),
]

ABSL_INCLUDE = (os.path.join("third_party", "abseil-cpp"),)
CARES_INCLUDE = (
    os.path.join("third_party", "cares", "cares", "include"),
    os.path.join("third_party", "cares"),
    os.path.join("third_party", "cares", "cares"),
)
if "darwin" in sys.platform:
    CARES_INCLUDE += (os.path.join("third_party", "cares", "config_darwin"),)
if "freebsd" in sys.platform:
    CARES_INCLUDE += (os.path.join("third_party", "cares", "config_freebsd"),)
if "linux" in sys.platform:
    CARES_INCLUDE += (os.path.join("third_party", "cares", "config_linux"),)
if "openbsd" in sys.platform:
    CARES_INCLUDE += (os.path.join("third_party", "cares", "config_openbsd"),)
UPB_INCLUDE = (os.path.join("third_party", "upb"),)
UPB_GRPC_GENERATED_INCLUDE = (
    os.path.join("src", "core", "ext", "upb-generated"),
)
UTF8_RANGE_INCLUDE = (os.path.join("third_party", "utf8_range"),)
PROTOBUF_INCLUDE = (os.path.join("third_party", "protobuf", "src"),)
ZLIB_INCLUDE = (os.path.join("third_party", "zlib"),)

# will be added to include path when building grpcio_observability
EXTENSION_INCLUDE_DIRECTORIES = (
    ABSL_INCLUDE
    + CARES_INCLUDE
    + UPB_INCLUDE
    + UPB_GRPC_GENERATED_INCLUDE
    + UTF8_RANGE_INCLUDE
    + PROTOBUF_INCLUDE
    + ZLIB_INCLUDE
)

CC_INCLUDES = [
] + list(EXTENSION_INCLUDE_DIRECTORIES)


# the target directory is relative to the grpcio_observability package root.
GRPCIO_OBSERVABILITY_ROOT_PREFIX = 'src/python/grpcio_observability/'

# Pairs of (source, target) directories to copy
# from the grpc repo root to the grpcio_observability build root.
COPY_FILES_SOURCE_TARGET_PAIRS = [
    ('include', 'grpc_root/include'),
    ('third_party/abseil-cpp/absl', 'third_party/abseil-cpp/absl'),
    ("third_party/protobuf/src", "third_party/protobuf/src"),
    ("third_party/utf8_range", "third_party/utf8_range"),
    ("third_party/cares", "third_party/cares"),
    ('third_party/upb', 'third_party/upb'),
    ('third_party/zlib', 'third_party/zlib'),
    ('src/core/lib', 'grpc_root/src/core/lib'),
    ('src/core/tsi', 'grpc_root/src/core/tsi'),
    # ('src/cpp/ext/filters/census', 'grpc_root/src/cpp/ext/filters/census'),
    # ('src/cpp/ext/gcp', 'grpc_root/src/cpp/ext/gcp'),
    ('src/core/ext/upb-generated', 'grpc_root/src/core/ext/upb-generated'),
    # ('src/core/ext/filters/backend_metrics', 'grpc_root/src/core/ext/filters/backend_metrics'),
    ('src/core/ext/filters/client_channel/lb_policy', 'grpc_root/src/core/ext/filters/client_channel/lb_policy'),
    # ('src/core/ext/filters/census', 'grpc_root/src/core/ext/filters/census'),
    # ('src/cpp/filters/census', 'grpc_root/src/cpp/filters/census'),
]

# grpc repo root
GRPC_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

# the directory under which to probe for the current protobuf commit SHA
GRPC_PROTOBUF_SUBMODULE_ROOT = os.path.join(GRPC_ROOT, 'third_party',
                                            'protobuf')

# the file to generate
GRPC_PYTHON_OBSERVABILITY_LIB_DEPS = os.path.join(GRPC_ROOT, 'src', 'python',
                                                  'grpcio_observability',
                                                  'observability_lib_deps.py')

# the script to run for getting dependencies
BAZEL_DEPS = os.path.join(
    GRPC_ROOT, "tools", "distrib", "python", "bazel_deps.sh"
)

# # the bazel target to scrape to get list of sources for the build
BAZEL_DEPS_QUERIES = [
    # '//src/python/grpcio_observability/grpc_observability:observability',
    '//:grpc_base',
]

def protobuf_submodule_commit_hash():
    """Gets the commit hash for the HEAD of the protobuf submodule currently
     checked out."""
    cwd = os.getcwd()
    os.chdir(GRPC_PROTOBUF_SUBMODULE_ROOT)
    output = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    os.chdir(cwd)
    return output.decode("ascii").splitlines()[0].strip()

def _bazel_query(query):
    """Runs 'bazel query' to collect source file info."""
    print('Running "bazel query %s"' % query)
    output = subprocess.check_output([BAZEL_DEPS, query])
    return output.decode("ascii").splitlines()


def _pretty_print_list(items):
    """Pretty print python list"""
    formatted = pprint.pformat(items, indent=4)
    # add newline after opening bracket (and fix indent of the next line)
    if formatted.startswith('['):
        formatted = formatted[0] + '\n ' + formatted[1:]
    # add newline before closing bracket
    if formatted.endswith(']'):
        formatted = formatted[:-1] + '\n' + formatted[-1]
    return formatted

INTERNNEL_LINKS = [('//src', 'grpc_root/src'),
                   ('//:src', 'grpc_root/src')]

def _bazel_name_to_file_path(name):
    """Transform bazel reference to source file name."""
    for link in EXTERNAL_LINKS:
        if name.startswith(link[0]):
            filepath = link[1] + name[len(link[0]):].replace(':', '/')

            # For some reason, the WKT sources (such as wrappers.pb.cc)
            # end up being reported by bazel as having an extra 'wkt/google/protobuf'
            # in path. Removing it makes the compilation pass.
            # TODO(jtattermusch) Get dir of this hack.
            return filepath.replace('wkt/google/protobuf/', '')
    for link in INTERNNEL_LINKS:
        if name.startswith(link[0]):
            filepath = link[1] + name[len(link[0]):].replace(':', '/')
            return filepath
    return None

ADDS = [
    'src/core/ext/upb-generated/envoy/admin/v3/certs.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/clusters.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/config_dump.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/config_dump_shared.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/init_dump.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/listeners.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/memory.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/metrics.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/mutex_stats.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/server_info.upb.c',
    'src/core/ext/upb-generated/envoy/admin/v3/tap.upb.c',
    'src/core/ext/upb-generated/envoy/annotations/deprecation.upb.c',
    'src/core/ext/upb-generated/envoy/annotations/resource.upb.c',
    'src/core/ext/upb-generated/envoy/config/accesslog/v3/accesslog.upb.c',
    'src/core/ext/upb-generated/envoy/config/bootstrap/v3/bootstrap.upb.c',
    'src/core/ext/upb-generated/envoy/config/cluster/v3/circuit_breaker.upb.c',
    'src/core/ext/upb-generated/envoy/config/cluster/v3/cluster.upb.c',
    'src/core/ext/upb-generated/envoy/config/cluster/v3/filter.upb.c',
    'src/core/ext/upb-generated/envoy/config/cluster/v3/outlier_detection.upb.c',
    'src/core/ext/upb-generated/envoy/config/common/matcher/v3/matcher.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/address.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/backoff.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/base.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/config_source.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/event_service_config.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/extension.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/grpc_method_list.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/grpc_service.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/health_check.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/http_uri.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/protocol.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/proxy_protocol.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/resolver.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/socket_option.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/substitution_format_string.upb.c',
    'src/core/ext/upb-generated/envoy/config/core/v3/udp_socket_config.upb.c',
    'src/core/ext/upb-generated/envoy/config/endpoint/v3/endpoint.upb.c',
    'src/core/ext/upb-generated/envoy/config/endpoint/v3/endpoint_components.upb.c',
    'src/core/ext/upb-generated/envoy/config/endpoint/v3/load_report.upb.c',
    'src/core/ext/upb-generated/envoy/config/listener/v3/api_listener.upb.c',
    'src/core/ext/upb-generated/envoy/config/listener/v3/listener.upb.c',
    'src/core/ext/upb-generated/envoy/config/listener/v3/listener_components.upb.c',
    'src/core/ext/upb-generated/envoy/config/listener/v3/quic_config.upb.c',
    'src/core/ext/upb-generated/envoy/config/listener/v3/udp_listener_config.upb.c',
    'src/core/ext/upb-generated/envoy/config/metrics/v3/metrics_service.upb.c',
    'src/core/ext/upb-generated/envoy/config/metrics/v3/stats.upb.c',
    'src/core/ext/upb-generated/envoy/config/overload/v3/overload.upb.c',
    'src/core/ext/upb-generated/envoy/config/rbac/v3/rbac.upb.c',
    'src/core/ext/upb-generated/envoy/config/route/v3/route.upb.c',
    'src/core/ext/upb-generated/envoy/config/route/v3/route_components.upb.c',
    'src/core/ext/upb-generated/envoy/config/route/v3/scoped_route.upb.c',
    'src/core/ext/upb-generated/envoy/config/tap/v3/common.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/datadog.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/dynamic_ot.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/http_tracer.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/lightstep.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/opencensus.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/opentelemetry.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/service.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/skywalking.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/trace.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/xray.upb.c',
    'src/core/ext/upb-generated/envoy/config/trace/v3/zipkin.upb.c',
    'src/core/ext/upb-generated/envoy/data/accesslog/v3/accesslog.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/clusters/aggregate/v3/cluster.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/filters/common/fault/v3/fault.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/filters/http/fault/v3/fault.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/filters/http/rbac/v3/rbac.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/filters/http/router/v3/router.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/filters/http/stateful_session/v3/stateful_session.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/filters/network/http_connection_manager/v3/http_connection_manager.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/http/stateful_session/cookie/v3/cookie.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/load_balancing_policies/client_side_weighted_round_robin/v3/client_side_weighted_round_robin.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/load_balancing_policies/common/v3/common.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/load_balancing_policies/pick_first/v3/pick_first.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/load_balancing_policies/ring_hash/v3/ring_hash.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/load_balancing_policies/wrr_locality/v3/wrr_locality.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/transport_sockets/tls/v3/cert.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/transport_sockets/tls/v3/common.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/transport_sockets/tls/v3/secret.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/transport_sockets/tls/v3/tls.upb.c',
    'src/core/ext/upb-generated/envoy/extensions/transport_sockets/tls/v3/tls_spiffe_validator_config.upb.c',
    'src/core/ext/upb-generated/envoy/service/discovery/v3/ads.upb.c',
    'src/core/ext/upb-generated/envoy/service/discovery/v3/discovery.upb.c',
    'src/core/ext/upb-generated/envoy/service/load_stats/v3/lrs.upb.c',
    'src/core/ext/upb-generated/envoy/service/status/v3/csds.upb.c',
    'src/core/ext/upb-generated/envoy/type/http/v3/cookie.upb.c',
    'src/core/ext/upb-generated/envoy/type/http/v3/path_transformation.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/filter_state.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/http_inputs.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/metadata.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/node.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/number.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/path.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/regex.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/status_code_input.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/string.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/struct.upb.c',
    'src/core/ext/upb-generated/envoy/type/matcher/v3/value.upb.c',
    'src/core/ext/upb-generated/envoy/type/metadata/v3/metadata.upb.c',
    'src/core/ext/upb-generated/envoy/type/tracing/v3/custom_tag.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/hash_policy.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/http.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/http_status.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/percent.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/range.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/ratelimit_strategy.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/ratelimit_unit.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/semantic_version.upb.c',
    'src/core/ext/upb-generated/envoy/type/v3/token_bucket.upb.c',
    'src/core/ext/upb-generated/google/api/annotations.upb.c',
    'src/core/ext/upb-generated/google/api/expr/v1alpha1/checked.upb.c',
    'src/core/ext/upb-generated/google/api/expr/v1alpha1/syntax.upb.c',
    'src/core/ext/upb-generated/google/api/http.upb.c',
    'src/core/ext/upb-generated/google/api/httpbody.upb.c',
    'src/core/ext/upb-generated/google/protobuf/any.upb.c',
    'src/core/ext/upb-generated/google/protobuf/descriptor.upb.c',
    'src/core/ext/upb-generated/google/protobuf/duration.upb.c',
    'src/core/ext/upb-generated/google/protobuf/empty.upb.c',
    'src/core/ext/upb-generated/google/protobuf/struct.upb.c',
    'src/core/ext/upb-generated/google/protobuf/timestamp.upb.c',
    'src/core/ext/upb-generated/google/protobuf/wrappers.upb.c',
    'src/core/ext/upb-generated/google/rpc/status.upb.c',
    'src/core/ext/upb-generated/opencensus/proto/trace/v1/trace_config.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/gcp/altscontext.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/gcp/handshaker.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/gcp/transport_security_common.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/health/v1/health.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/lb/v1/load_balancer.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/lookup/v1/rls.upb.c',
    'src/core/ext/upb-generated/src/proto/grpc/lookup/v1/rls_config.upb.c',
    'src/core/ext/upb-generated/udpa/annotations/migrate.upb.c',
    'src/core/ext/upb-generated/udpa/annotations/security.upb.c',
    'src/core/ext/upb-generated/udpa/annotations/sensitive.upb.c',
    'src/core/ext/upb-generated/udpa/annotations/status.upb.c',
    'src/core/ext/upb-generated/udpa/annotations/versioning.upb.c',
    'src/core/ext/upb-generated/validate/validate.upb.c',
    'src/core/ext/upb-generated/xds/annotations/v3/migrate.upb.c',
    'src/core/ext/upb-generated/xds/annotations/v3/security.upb.c',
    'src/core/ext/upb-generated/xds/annotations/v3/sensitive.upb.c',
    'src/core/ext/upb-generated/xds/annotations/v3/status.upb.c',
    'src/core/ext/upb-generated/xds/annotations/v3/versioning.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/authority.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/cidr.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/collection_entry.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/context_params.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/extension.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/resource.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/resource_locator.upb.c',
    'src/core/ext/upb-generated/xds/core/v3/resource_name.upb.c',
    'src/core/ext/upb-generated/xds/data/orca/v3/orca_load_report.upb.c',
    'src/core/ext/upb-generated/xds/service/orca/v3/orca.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/cel.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/domain.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/http_inputs.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/ip.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/matcher.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/range.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/regex.upb.c',
    'src/core/ext/upb-generated/xds/type/matcher/v3/string.upb.c',
    'src/core/ext/upb-generated/xds/type/v3/cel.upb.c',
    'src/core/ext/upb-generated/xds/type/v3/range.upb.c',
    'src/core/ext/upb-generated/xds/type/v3/typed_struct.upb.c',
    'third_party/zlib/adler32.c',
    'third_party/zlib/compress.c',
    'third_party/zlib/crc32.c',
    'third_party/zlib/deflate.c',
    'third_party/zlib/gzclose.c',
    'third_party/zlib/gzlib.c',
    'third_party/zlib/gzread.c',
    'third_party/zlib/gzwrite.c',
    'third_party/zlib/infback.c',
    'third_party/zlib/inffast.c',
    'third_party/zlib/inflate.c',
    'third_party/zlib/inftrees.c',
    'third_party/zlib/trees.c',
    'third_party/zlib/uncompr.c',
    'third_party/zlib/zutil.c',
    'third_party/upb/upb/base/status.c',
    'third_party/upb/upb/collections/array.c',
    'third_party/upb/upb/collections/map.c',
    'third_party/upb/upb/collections/map_sorter.c',
    'third_party/upb/upb/hash/common.c',
    'third_party/upb/upb/json/decode.c',
    'third_party/upb/upb/json/encode.c',
    'third_party/upb/upb/lex/atoi.c',
    'third_party/upb/upb/lex/round_trip.c',
    'third_party/upb/upb/lex/strtod.c',
    'third_party/upb/upb/lex/unicode.c',
    'third_party/upb/upb/mem/alloc.c',
    'third_party/upb/upb/mem/arena.c',
    'third_party/upb/upb/message/accessors.c',
    'third_party/upb/upb/message/message.c',
    'third_party/upb/upb/mini_table/common.c',
    'third_party/upb/upb/mini_table/decode.c',
    'third_party/upb/upb/mini_table/encode.c',
    'third_party/upb/upb/mini_table/extension_registry.c',
    'third_party/upb/upb/reflection/def_builder.c',
    'third_party/upb/upb/reflection/def_pool.c',
    'third_party/upb/upb/reflection/def_type.c',
    'third_party/upb/upb/reflection/desc_state.c',
    'third_party/upb/upb/reflection/enum_def.c',
    'third_party/upb/upb/reflection/enum_reserved_range.c',
    'third_party/upb/upb/reflection/enum_value_def.c',
    'third_party/upb/upb/reflection/extension_range.c',
    'third_party/upb/upb/reflection/field_def.c',
    'third_party/upb/upb/reflection/file_def.c',
    'third_party/upb/upb/reflection/message.c',
    'third_party/upb/upb/reflection/message_def.c',
    'third_party/upb/upb/reflection/message_reserved_range.c',
    'third_party/upb/upb/reflection/method_def.c',
    'third_party/upb/upb/reflection/oneof_def.c',
    'third_party/upb/upb/reflection/service_def.c',
    'third_party/upb/upb/text/encode.c',
    'third_party/upb/upb/wire/decode.c',
    'third_party/upb/upb/wire/decode_fast.c',
    'third_party/upb/upb/wire/encode.c',
    'third_party/upb/upb/wire/eps_copy_input_stream.c',
    'third_party/upb/upb/wire/reader.c',
    'third_party/cares/cares/src/lib/ares__addrinfo2hostent.c',
    'third_party/cares/cares/src/lib/ares__addrinfo_localhost.c',
    'third_party/cares/cares/src/lib/ares__close_sockets.c',
    'third_party/cares/cares/src/lib/ares__get_hostent.c',
    'third_party/cares/cares/src/lib/ares__parse_into_addrinfo.c',
    'third_party/cares/cares/src/lib/ares__read_line.c',
    'third_party/cares/cares/src/lib/ares__readaddrinfo.c',
    'third_party/cares/cares/src/lib/ares__sortaddrinfo.c',
    'third_party/cares/cares/src/lib/ares__timeval.c',
    'third_party/cares/cares/src/lib/ares_android.c',
    'third_party/cares/cares/src/lib/ares_cancel.c',
    'third_party/cares/cares/src/lib/ares_create_query.c',
    'third_party/cares/cares/src/lib/ares_data.c',
    'third_party/cares/cares/src/lib/ares_destroy.c',
    'third_party/cares/cares/src/lib/ares_expand_name.c',
    'third_party/cares/cares/src/lib/ares_expand_string.c',
    'third_party/cares/cares/src/lib/ares_fds.c',
    'third_party/cares/cares/src/lib/ares_free_hostent.c',
    'third_party/cares/cares/src/lib/ares_free_string.c',
    'third_party/cares/cares/src/lib/ares_freeaddrinfo.c',
    'third_party/cares/cares/src/lib/ares_getaddrinfo.c',
    'third_party/cares/cares/src/lib/ares_getenv.c',
    'third_party/cares/cares/src/lib/ares_gethostbyaddr.c',
    'third_party/cares/cares/src/lib/ares_gethostbyname.c',
    'third_party/cares/cares/src/lib/ares_getnameinfo.c',
    'third_party/cares/cares/src/lib/ares_getsock.c',
    'third_party/cares/cares/src/lib/ares_init.c',
    'third_party/cares/cares/src/lib/ares_library_init.c',
    'third_party/cares/cares/src/lib/ares_llist.c',
    'third_party/cares/cares/src/lib/ares_mkquery.c',
    'third_party/cares/cares/src/lib/ares_nowarn.c',
    'third_party/cares/cares/src/lib/ares_options.c',
    'third_party/cares/cares/src/lib/ares_parse_a_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_aaaa_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_caa_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_mx_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_naptr_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_ns_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_ptr_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_soa_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_srv_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_txt_reply.c',
    'third_party/cares/cares/src/lib/ares_parse_uri_reply.c',
    'third_party/cares/cares/src/lib/ares_platform.c',
    'third_party/cares/cares/src/lib/ares_process.c',
    'third_party/cares/cares/src/lib/ares_query.c',
    'third_party/cares/cares/src/lib/ares_rand.c',
    'third_party/cares/cares/src/lib/ares_search.c',
    'third_party/cares/cares/src/lib/ares_send.c',
    'third_party/cares/cares/src/lib/ares_strcasecmp.c',
    'third_party/cares/cares/src/lib/ares_strdup.c',
    'third_party/cares/cares/src/lib/ares_strerror.c',
    'third_party/cares/cares/src/lib/ares_strsplit.c',
    'third_party/cares/cares/src/lib/ares_timeout.c',
    'third_party/cares/cares/src/lib/ares_version.c',
    'third_party/cares/cares/src/lib/ares_writev.c',
    'third_party/cares/cares/src/lib/bitncmp.c',
    'third_party/cares/cares/src/lib/inet_net_pton.c',
    'third_party/cares/cares/src/lib/inet_ntop.c',
    'third_party/cares/cares/src/lib/windows_port.c',
]

def _generate_deps_file_content():
    """Returns the data structure with dependencies of protoc as python code."""
    cc_files_output = []
    for target in BAZEL_DEPS_QUERIES:
        cc_files_output += _bazel_query(target)

    # Collect .cc files (that will be later included in the native extension build)
    cc_files = set()
    for name in cc_files_output:
        if name.endswith(".cc"):
            filepath = _bazel_name_to_file_path(name)
            if filepath and 'third_party/protobuf' not in filepath:
                cc_files.add(filepath)

    for path in ADDS:
        actual_path = path
        if 'third_party' not in actual_path:
            actual_path = os.path.join("grpc_root", path)
        cc_files.add(actual_path)

    commit_hash = protobuf_submodule_commit_hash()
    commit_hash_expr = COMMIT_HASH_PREFIX + commit_hash + COMMIT_HASH_SUFFIX

    deps_file_content = DEPS_FILE_CONTENT.format(
        cc_files=_pretty_print_list(sorted(list(cc_files))),
        # proto_files=_pretty_print_list(sorted(set(proto_files))),
        cc_includes=_pretty_print_list(CC_INCLUDES),
        # proto_include=repr(PROTO_INCLUDE),
        commit_hash_expr=commit_hash_expr,
    )
    return deps_file_content


def _copy_source_tree(source, target):
    """Copies source directory to a given target directory."""
    print('Copying contents of %s to %s' % (source, target))
    for source_dir, _, files in os.walk(source):
        target_dir = os.path.abspath(
            os.path.join(target, os.path.relpath(source_dir, source)))
        try:
            os.makedirs(target_dir)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise
        for relative_file in files:
            source_file = os.path.abspath(
                os.path.join(source_dir, relative_file))
            target_file = os.path.abspath(
                os.path.join(target_dir, relative_file))
            shutil.copyfile(source_file, target_file)

def main():
    os.chdir(GRPC_ROOT)

    # Step 1:
    # In order to be able to build the grpcio_observability package, we need the source code for the plugins
    # and its dependencies to be available under the build root of the grpcio_observability package.
    # So we simply copy all the necessary files where the build will expect them to be.
    for source, target in COPY_FILES_SOURCE_TARGET_PAIRS:
        # convert the slashes in the relative path to platform-specific path dividers.
        # All paths are relative to GRPC_ROOT
        source_abs = os.path.join(GRPC_ROOT, os.path.join(*source.split('/')))
        # for targets, add grpcio_observability root prefix
        target = GRPCIO_OBSERVABILITY_ROOT_PREFIX + target
        target_abs = os.path.join(GRPC_ROOT, os.path.join(*target.split('/')))
        _copy_source_tree(source_abs, target_abs)
    print('The necessary source files were copied under the grpcio_observability package root.')

    # Step 2:
    # Extract build metadata from bazel build (by running "bazel query")
    # and populate the observability_lib_deps.py file with python-readable data structure
    # that will be used by grpcio_observability's setup.py (so it knows how to configure
    # the native build for the codegen plugin)
    try:
        print('Invoking "bazel query" to gather the dependencies.')
        observability_lib_deps_content = _generate_deps_file_content()
    except Exception as error:
        # We allow this script to succeed even if we couldn't get the dependencies,
        # as then we can assume that even without a successful bazel run the
        # dependencies currently in source control are 'good enough'.
        sys.stderr.write("Got non-fatal error:\n")
        traceback.print_exc(file=sys.stderr)
        return
    # If we successfully got the dependencies, truncate and rewrite the deps file.
    with open(GRPC_PYTHON_OBSERVABILITY_LIB_DEPS, 'w') as deps_file:
        deps_file.write(observability_lib_deps_content)
    print('File "%s" updated.' % GRPC_PYTHON_OBSERVABILITY_LIB_DEPS)
    print('Done.')


if __name__ == '__main__':
    main()
