#!/usr/bin/env python3

# Copyright 2016 gRPC authors.
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

import argparse
import errno
import filecmp
import glob
import os
import os.path
import pprint
import shutil
import subprocess
import sys
import traceback
import uuid

# the template for the content of protoc_lib_deps.py
DEPS_FILE_CONTENT = """
# Copyright 2017 gRPC authors.
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

# AUTO-GENERATED BY make_grpcio_tools.py!
CC_FILES={cc_files}

PROTO_FILES={proto_files}

CC_INCLUDES={cc_includes}
PROTO_INCLUDE={proto_include}

{commit_hash_expr}
"""

# expose commit hash suffix and prefix for check_grpcio_tools.py
COMMIT_HASH_PREFIX = 'PROTOBUF_SUBMODULE_VERSION="'
COMMIT_HASH_SUFFIX = '"'

EXTERNAL_LINKS = [
    ("@com_google_absl//", "third_party/abseil-cpp/"),
    ("@com_google_protobuf//", "third_party/protobuf/"),
]

PROTOBUF_PROTO_PREFIX = "@com_google_protobuf//src/"

# will be added to include path when building grpcio_tools
CC_INCLUDES = [
    os.path.join("third_party", "abseil-cpp"),
    os.path.join("third_party", "protobuf", "src"),
    os.path.join("third_party", "protobuf", "third_party", "utf8_range"),
]

# include path for .proto files
PROTO_INCLUDE = os.path.join("third_party", "protobuf", "src")

# the target directory is relative to the grpcio_tools package root.
GRPCIO_TOOLS_ROOT_PREFIX = "tools/distrib/python/grpcio_tools/"

# Pairs of (source, target) directories to copy
# from the grpc repo root to the grpcio_tools build root.
COPY_FILES_SOURCE_TARGET_PAIRS = [
    ("include", "grpc_root/include"),
    ("src/compiler", "grpc_root/src/compiler"),
    ("third_party/abseil-cpp/absl", "third_party/abseil-cpp/absl"),
    ("third_party/protobuf/src", "third_party/protobuf/src"),
    (
        "third_party/protobuf/third_party/utf8_range",
        "third_party/protobuf/third_party/utf8_range",
    ),
]

DELETE_TARGETS_ON_CLEANUP = ["third_party"]

# grpc repo root
GRPC_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)

# the directory under which to probe for the current protobuf commit SHA
GRPC_PROTOBUF_SUBMODULE_ROOT = os.path.join(
    GRPC_ROOT, "third_party", "protobuf"
)

# the file to generate
GRPC_PYTHON_PROTOC_LIB_DEPS = os.path.join(
    GRPC_ROOT,
    "tools",
    "distrib",
    "python",
    "grpcio_tools",
    "protoc_lib_deps.py",
)

# the script to run for getting dependencies
BAZEL_DEPS = os.path.join(
    GRPC_ROOT, "tools", "distrib", "python", "bazel_deps.sh"
)

# the bazel target to scrape to get list of sources for the build
BAZEL_DEPS_PROTOC_LIB_QUERY = "@com_google_protobuf//:protoc_lib"

BAZEL_DEPS_COMMON_PROTOS_QUERIES = [
    "@com_google_protobuf//:well_known_type_protos",
    # has both plugin.proto and descriptor.proto
    "@com_google_protobuf//:compiler_plugin_proto",
]


def protobuf_submodule_commit_hash():
    """Gets the commit hash for the HEAD of the protobuf submodule currently
    checked out."""
    cwd = os.getcwd()
    os.chdir(GRPC_PROTOBUF_SUBMODULE_ROOT)
    output = subprocess.check_output(["git", "rev-parse", "HEAD"])
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
    if formatted.startswith("["):
        formatted = formatted[0] + "\n " + formatted[1:]
    # add newline before closing bracket
    if formatted.endswith("]"):
        formatted = formatted[:-1] + "\n" + formatted[-1]
    return formatted


def _bazel_name_to_file_path(name):
    """Transform bazel reference to source file name."""
    for link in EXTERNAL_LINKS:
        if name.startswith(link[0]):
            filepath = link[1] + name[len(link[0]) :].replace(":", "/")

            # For some reason, the WKT sources (such as wrappers.pb.cc)
            # end up being reported by bazel as having an extra 'wkt/google/protobuf'
            # in path. Removing it makes the compilation pass.
            # TODO(jtattermusch) Get dir of this hack.
            return filepath.replace("wkt/google/protobuf/", "")
    return None


def _generate_deps_file_content():
    """Returns the data structure with dependencies of protoc as python code."""
    cc_files_output = _bazel_query(BAZEL_DEPS_PROTOC_LIB_QUERY)

    # Collect .cc files (that will be later included in the native extension build)
    cc_files = []
    for name in cc_files_output:
        if name.endswith(".cc"):
            filepath = _bazel_name_to_file_path(name)
            if filepath:
                cc_files.append(filepath)

    # Collect list of .proto files that will be bundled in the grpcio_tools package.
    raw_proto_files = []
    for target in BAZEL_DEPS_COMMON_PROTOS_QUERIES:
        raw_proto_files += _bazel_query(target)
    proto_files = [
        name[len(PROTOBUF_PROTO_PREFIX) :].replace(":", "/")
        for name in raw_proto_files
        if name.endswith(".proto") and name.startswith(PROTOBUF_PROTO_PREFIX)
    ]

    commit_hash = protobuf_submodule_commit_hash()
    commit_hash_expr = COMMIT_HASH_PREFIX + commit_hash + COMMIT_HASH_SUFFIX

    deps_file_content = DEPS_FILE_CONTENT.format(
        cc_files=_pretty_print_list(sorted(cc_files)),
        proto_files=_pretty_print_list(sorted(set(proto_files))),
        cc_includes=_pretty_print_list(CC_INCLUDES),
        proto_include=repr(PROTO_INCLUDE),
        commit_hash_expr=commit_hash_expr,
    )
    return deps_file_content


def _copy_source_tree(source, target):
    """Copies source directory to a given target directory."""
    print("Copying contents of %s to %s" % (source, target))
    # TODO(jtattermusch): It is unclear why this legacy code needs to copy
    # the source directory to the target via the following boilerplate.
    # Should this code be simplified?
    for source_dir, _, files in os.walk(source):
        target_dir = os.path.abspath(
            os.path.join(target, os.path.relpath(source_dir, source))
        )
        try:
            os.makedirs(target_dir)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise
        for relative_file in files:
            source_file = os.path.abspath(
                os.path.join(source_dir, relative_file)
            )
            target_file = os.path.abspath(
                os.path.join(target_dir, relative_file)
            )
            shutil.copyfile(source_file, target_file)


def _delete_source_tree(target):
    """Deletes the copied target directory."""
    target = GRPCIO_TOOLS_ROOT_PREFIX + target
    target_abs = os.path.join(*target.split("/"))
    print("Deleting copied folder %s" % (target_abs))
    shutil.rmtree(target_abs, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()
    # In Step 1 below, the third_party folder is copied to a location required
    # by the build scripts. This folder does not need to be committed to the
    # repo, so you can pass `--cleanup_third_party` in automated scripts to
    # ensure that the temporary folders are deleted after the script runs.
    # See Jan's TODO in _copy_source_tree above.
    parser.add_argument(
        "--cleanup_third_party",
        default=False,
        action="store_true",
        help="Delete the temporary third_party folder",
    )
    args = parser.parse_args()
    os.chdir(GRPC_ROOT)

    # Step 1:
    # In order to be able to build the grpcio_tools package, we need the source code for the codegen plugins
    # and its dependencies to be available under the build root of the grpcio_tools package.
    # So we simply copy all the necessary files where the build will expect them to be.
    for source, target in COPY_FILES_SOURCE_TARGET_PAIRS:
        # convert the slashes in the relative path to platform-specific path dividers.
        # All paths are relative to GRPC_ROOT
        source_abs = os.path.join(GRPC_ROOT, os.path.join(*source.split("/")))
        # for targets, add grpcio_tools root prefix
        target = GRPCIO_TOOLS_ROOT_PREFIX + target
        target_abs = os.path.join(GRPC_ROOT, os.path.join(*target.split("/")))

        _copy_source_tree(source_abs, target_abs)
    print(
        "The necessary source files were copied under the grpcio_tools package"
        " root."
    )
    print()

    # Step 2:
    # Extract build metadata from bazel build (by running "bazel query")
    # and populate the protoc_lib_deps.py file with python-readable data structure
    # that will be used by grpcio_tools's setup.py (so it knows how to configure
    # the native build for the codegen plugin)
    try:
        print('Invoking "bazel query" to gather the protobuf dependencies.')
        protoc_lib_deps_content = _generate_deps_file_content()
    except Exception as error:
        # We allow this script to succeed even if we couldn't get the dependencies,
        # as then we can assume that even without a successful bazel run the
        # dependencies currently in source control are 'good enough'.
        sys.stderr.write("Got non-fatal error:\n")
        traceback.print_exc(file=sys.stderr)
        return
    # If we successfully got the dependencies, truncate and rewrite the deps file.
    with open(GRPC_PYTHON_PROTOC_LIB_DEPS, "w") as deps_file:
        deps_file.write(protoc_lib_deps_content)
    print('File "%s" updated.' % GRPC_PYTHON_PROTOC_LIB_DEPS)
    if args.cleanup_third_party:
        for target in DELETE_TARGETS_ON_CLEANUP:
            _delete_source_tree(target)
    print("Done.")


if __name__ == "__main__":
    main()
