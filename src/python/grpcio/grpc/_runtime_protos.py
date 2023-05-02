# Copyright 2020 The gRPC authors.
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

import sys
import types
from typing import Tuple, Union, cast

_REQUIRED_SYMBOLS = ("_protos", "_services", "_protos_and_services")
_MINIMUM_VERSION = (3, 5, 0)

_UNINSTALLED_TEMPLATE = "Install the grpcio-tools package (1.32.0+) to use the {} function."
_VERSION_ERROR_TEMPLATE = "The {} function is only on available on Python 3.X interpreters."


def _has_runtime_proto_symbols(mod: types.ModuleType) -> bool:
    return all(hasattr(mod, sym) for sym in _REQUIRED_SYMBOLS)


def _is_grpc_tools_importable() -> bool:
    try:
        import grpc_tools  # pylint: disable=unused-import # pytype: disable=import-error
        return True
    except ImportError as e:
        # NOTE: It's possible that we're encountering a transitive ImportError, so
        # we check for that and re-raise if so.
        if "grpc_tools" not in e.args[0]:
            raise
        return False


def _call_with_lazy_import(
    fn_name: str, protobuf_path: str
) -> Union[types.ModuleType, Tuple[types.ModuleType, types.ModuleType]]:
    """Calls one of the three functions, lazily importing grpc_tools.

    Args:
      fn_name: The name of the function to import from grpc_tools.protoc.
      protobuf_path: The path to import.

    Returns:
      The appropriate module object.
    """
    if sys.version_info < _MINIMUM_VERSION:
        raise NotImplementedError(_VERSION_ERROR_TEMPLATE.format(fn_name))
    else:
        if not _is_grpc_tools_importable():
            raise NotImplementedError(_UNINSTALLED_TEMPLATE.format(fn_name))
        import grpc_tools.protoc  # pytype: disable=import-error
        if _has_runtime_proto_symbols(grpc_tools.protoc):
            fn = getattr(grpc_tools.protoc, '_' + fn_name)
            return fn(protobuf_path)
        else:
            raise NotImplementedError(_UNINSTALLED_TEMPLATE.format(fn_name))


def protos(protobuf_path: str) -> types.ModuleType:  # pylint: disable=unused-argument
    """Returns a module generated by the indicated .proto file.

    THIS IS AN EXPERIMENTAL API.

    Use this function to retrieve classes corresponding to message
    definitions in the .proto file.

    To inspect the contents of the returned module, use the dir function.
    For example:

    ```
    protos = grpc.protos("foo.proto")
    print(dir(protos))
    ```

    The returned module object corresponds to the _pb2.py file generated
    by protoc. The path is expected to be relative to an entry on sys.path
    and all transitive dependencies of the file should also be resolveable
    from an entry on sys.path.

    To completely disable the machinery behind this function, set the
    GRPC_PYTHON_DISABLE_DYNAMIC_STUBS environment variable to "true".

    Args:
      protobuf_path: The path to the .proto file on the filesystem. This path
        must be resolveable from an entry on sys.path and so must all of its
        transitive dependencies.

    Returns:
      A module object corresponding to the message code for the indicated
      .proto file. Equivalent to a generated _pb2.py file.
    """
    return cast(types.ModuleType,
                _call_with_lazy_import("protos", protobuf_path))


def services(protobuf_path: str) -> types.ModuleType:  # pylint: disable=unused-argument
    """Returns a module generated by the indicated .proto file.

    THIS IS AN EXPERIMENTAL API.

    Use this function to retrieve classes and functions corresponding to
    service definitions in the .proto file, including both stub and servicer
    definitions.

    To inspect the contents of the returned module, use the dir function.
    For example:

    ```
    services = grpc.services("foo.proto")
    print(dir(services))
    ```

    The returned module object corresponds to the _pb2_grpc.py file generated
    by protoc. The path is expected to be relative to an entry on sys.path
    and all transitive dependencies of the file should also be resolveable
    from an entry on sys.path.

    To completely disable the machinery behind this function, set the
    GRPC_PYTHON_DISABLE_DYNAMIC_STUBS environment variable to "true".

    Args:
      protobuf_path: The path to the .proto file on the filesystem. This path
        must be resolveable from an entry on sys.path and so must all of its
        transitive dependencies.

    Returns:
      A module object corresponding to the stub/service code for the indicated
      .proto file. Equivalent to a generated _pb2_grpc.py file.
    """
    return cast(types.ModuleType,
                _call_with_lazy_import("services", protobuf_path))


def protos_and_services(
    protobuf_path: str
) -> Tuple[types.ModuleType, types.ModuleType]:  # pylint: disable=unused-argument
    """Returns a 2-tuple of modules corresponding to protos and services.

    THIS IS AN EXPERIMENTAL API.

    The return value of this function is equivalent to a call to protos and a
    call to services.

    To completely disable the machinery behind this function, set the
    GRPC_PYTHON_DISABLE_DYNAMIC_STUBS environment variable to "true".

    Args:
      protobuf_path: The path to the .proto file on the filesystem. This path
        must be resolveable from an entry on sys.path and so must all of its
        transitive dependencies.

    Returns:
      A 2-tuple of module objects corresponding to (protos(path), services(path)).
    """
    protos_and_services_modules = _call_with_lazy_import(
        "protos_and_services", protobuf_path)
    return cast(Tuple[types.ModuleType, types.ModuleType],
                protos_and_services_modules)
