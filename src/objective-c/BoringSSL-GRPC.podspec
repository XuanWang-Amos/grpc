

# This file has been automatically generated from a template file.
# Please make modifications to
# `templates/src/objective-c/BoringSSL-GRPC.podspec.template` instead. This
# file can be regenerated from the template by running
# `tools/buildgen/generate_projects.sh`.

# BoringSSL CocoaPods podspec

# Copyright 2015, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Pod::Spec.new do |s|
  s.name     = 'BoringSSL-GRPC'
  version = '0.0.33'
  s.version  = version
  s.summary  = 'BoringSSL is a fork of OpenSSL that is designed to meet Google\'s needs.'
  # Adapted from the homepage:
  s.description = <<-DESC
    BoringSSL is a fork of OpenSSL that is designed to meet Google's needs.

    Although BoringSSL is an open source project, it is not intended for general use, as OpenSSL is.
    We don't recommend that third parties depend upon it. Doing so is likely to be frustrating
    because there are no guarantees of API stability. Only the latest version of this pod is
    supported, and every new version is a new major version.

    We update Google libraries and programs that use BoringSSL as needed when deciding to make API
    changes. This allows us to mostly avoid compromises in the name of compatibility. It works for
    us, but it may not work for you.

    As a Cocoapods pod, it has the advantage over OpenSSL's pods that the library doesn't need to
    be precompiled. This eliminates the 10 - 20 minutes of wait the first time a user does "pod
    install", lets it be used as a dynamic framework (pending solution of Cocoapods' issue #4605),
    and works with bitcode automatically. It's also thought to be smaller than OpenSSL (which takes
    1MB - 2MB per ARM architecture), but we don't have specific numbers yet.

    BoringSSL arose because Google used OpenSSL for many years in various ways and, over time, built
    up a large number of patches that were maintained while tracking upstream OpenSSL. As Google's
    product portfolio became more complex, more copies of OpenSSL sprung up and the effort involved
    in maintaining all these patches in multiple places was growing steadily.

    Currently BoringSSL is the SSL library in Chrome/Chromium, Android (but it's not part of the
    NDK) and a number of other apps/programs.
  DESC
  s.homepage = 'https://github.com/google/boringssl'
  s.license  = { :type => 'Mixed', :file => 'LICENSE' }
  # "The name and email addresses of the library maintainers, not the Podspec maintainer."
  s.authors  = 'Adam Langley', 'David Benjamin', 'Matt Braithwaite'

  s.source = {
    :git => 'https://github.com/google/boringssl.git',
    :commit => "de02f415b10fcd5545870a50892a43e9b047295a",
  }

  s.ios.deployment_target = '10.0'
  s.osx.deployment_target = '10.12'
  s.tvos.deployment_target = '12.0'
  s.watchos.deployment_target = '6.0'

  name = 'openssl_grpc'

  # When creating a dynamic framework, name it openssl.framework instead of BoringSSL.framework.
  # This lets users write their includes like `#include <openssl/ssl.h>` as opposed to `#include
  # <BoringSSL/ssl.h>`.
  s.module_name = name

  # When creating a dynamic framework, copy the headers under `include/openssl/` into the root of
  # the `Headers/` directory of the framework (i.e., not under `Headers/include/openssl`).
  #
  # TODO(jcanizales): Debug why this doesn't work on macOS.
  s.header_mappings_dir = 'src/include/openssl'

  # The above has an undesired effect when creating a static library: It forces users to write
  # includes like `#include <BoringSSL/ssl.h>`. `s.header_dir` adds a path prefix to that, and
  # because Cocoapods lets omit the pod name when including headers of static libraries, the
  # following lets users write `#include <openssl/ssl.h>`.
  s.header_dir = name

  # We don't need to inhibit all warnings; only -Wno-shorten-64-to-32. But Cocoapods' linter doesn't
  # want that for some reason.
  s.compiler_flags = '-DOPENSSL_NO_ASM', '-GCC_WARN_INHIBIT_ALL_WARNINGS', '-w', '-DBORINGSSL_PREFIX=GRPC'
  s.requires_arc = false

  # Like many other C libraries, BoringSSL has its public headers under `include/<libname>/` and its
  # sources and private headers in other directories outside `include/`. Cocoapods' linter doesn't
  # allow any header to be listed outside the `header_mappings_dir` (even though doing so works in
  # practice). Because we need our `header_mappings_dir` to be `include/openssl/` for the reason
  # mentioned above, we work around the linter limitation by dividing the pod into two subspecs, one
  # for public headers and the other for implementation. Each gets its own `header_mappings_dir`,
  # making the linter happy.
  s.subspec 'Interface' do |ss|
    ss.header_mappings_dir = 'src/include/openssl'
    ss.private_header_files = 'src/include/openssl/time.h'
    ss.source_files = 'src/include/openssl/*.h'
  end
  s.subspec 'Implementation' do |ss|
    ss.header_mappings_dir = 'src'

    ss.resource_bundles = {
      s.module_name => 'src/PrivacyInfo.xcprivacy'
    }

    ss.source_files = 'src/ssl/*.{h,c,cc}',
                      'src/ssl/**/*.{h,c,cc}',
                      'src/crypto/*.{h,c,cc}',
                      'src/crypto/**/*.{h,c,cc}',
                      # We have to include fiat because spake25519 depends on it
                      'src/third_party/fiat/*.{h,c,cc}',
                      # Include the err_data.c pre-generated in boringssl's master-with-bazel branch
                      'err_data.c'

    ss.private_header_files = 'src/ssl/*.h',
                              'src/ssl/**/*.h',
                              'src/crypto/*.h',
                              'src/crypto/**/*.h',
                              'src/third_party/fiat/*.h'
    # bcm.c includes other source files, creating duplicated symbols. Since it is not used, we
    # explicitly exclude it from the pod.
    # TODO (mxyan): Work with BoringSSL team to remove this hack.
    ss.exclude_files = 'src/crypto/fipsmodule/bcm.c',
                       'src/**/*_test.*',
                       'src/**/test_*.*',
                       'src/**/test/*.*'

    ss.dependency "#{s.name}/Interface", version
  end

  s.pod_target_xcconfig = {
    # Do not let src/include/openssl/time.h override system API
    'USE_HEADERMAP' => 'NO',
  }

  s.prepare_command = <<-END_OF_COMMAND
    set -e

    # To avoid symbol conflict with OpenSSL, gRPC needs to rename all the BoringSSL symbols with a
    # prefix. This is done with BoringSSL's BORINGSSL_PREFIX mechanism
    # (https://github.com/google/boringssl/blob/75148d7abf12bdd1797fec3c5da9a21963703516/BUILDING.md#building-with-prefixed-symbols).
    # The required prefix header file boringssl_prefix_symbols.h is not part of BoringSSL repo at
    # this moment. It has to be generated by BoringSSL's users and be injected to BoringSSL build.
    # gRPC generates this file in script /tools/distrib/upgrade_boringssl_objc.sh. This script
    # outputs a gzip+base64 encoded version of boringssl_prefix_symbols.h because of Cocoapods'
    # limit on the 'prepare_command' field length. The encoded header is generated from
    # /src/boringssl/boringssl_prefix_symbols.h. Here we decode the content and inject the header to
    # the correct location in BoringSSL.
    case "$(uname)" in
      Darwin) opts="" ;;
           *) opts="--ignore-garbage" ;;
    esac
    base64 --decode $opts <<EOF | gunzip > src/include/openssl/boringssl_prefix_symbols.h
      H4sICAAAAAAC/2JvcmluZ3NzbF9wcmVmaXhfc3ltYm9scy5oALS9XXPbuJaofT+/wnXm5kzVrpnYidPu
      986xlY4mju0tKT2duWFREmRzhyIVgvJH//oDkJSIj7VArgW/VbtmOpaeZ1EAiC+CwH/918mDKESV1mJ9
      snw9/iNZllVWPEiZJ7tKbLKX5FGka1H9p3w8KYuTT82n8/nNyarcbrP6/ztZi3dnmw+n58vTd5vV+vz8
      w/nFb+/S83cXv5+lH96L35fvPvx29vt5+m//9l//dXJV7l6r7OGxPvm/q/84OXt3evGPkz/K8iEXJ9Ni
      9Z/qK/pb96LaZlJmKl5dnuyl+IeKtnv9x8m2XGcb9f/TYv1fZXWyzmRdZct9LU7qx0yeyHJTP6eVONmo
      D9PiVbt2+2pXSnHynNXqB1TN/y/39clGiBOFPIpK6F9fpYVKiH+c7KryKVurJKkf01r9H3GSLssnoU2r
      47UXZZ2thL6KNu6uv97DR7udSKuTrDhJ81yTmZCHX7f4MjmZ331e/M/lbHIynZ/cz+7+nF5Prk/+z+Vc
      /fv/nFzeXjdfuvy++HI3O7mezq9uLqff5ieXNzcnippd3i6mk7l2/c908eVkNvnjcqaQO0UpX+++vbr5
      fj29/aMBp9/ub6YqSi84ufusHd8ms6sv6i+Xn6Y308WPJvzn6eJ2Mp//p3Kc3N6dTP6c3C5O5l+0x7iy
      T5OTm+nlp5vJyWf1r8vbH1o3v59cTS9v/qGueza5WvxDKQ7/pb50dXc7n/zzu9Kp75xcX367/ENfSEMf
      /tn8sC+Xi/mdijtTP2/+/Wahf8bn2d23k5u7ub7yk+/ziYpxubjUtEpDdcnzfyhuoi5wpq/7Uv3vajG9
      u9U+BajQi9mlvo7byR830z8mt1cTzd41wOJupr77fd4x/zi5nE3nOujd94Wm77SzKcJ3t7eT5jtt6uv0
      UNfSXMVkphLi22Uj/mznxn825f/T3Uw51e2TXF5fJ/ezyefpXye7VNZCntTP5YkqekWdbTJRSVV4VOEv
      C6EyodZFTBXqrdR/0KKs1nerLnHl5mSbrqryRLzs0qIphOp/WS1P0uphv1U+ebIUChZNIHX3/ue//fta
      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
    EOF

    # PrivacyInfo.xcprivacy is not part of BoringSSL repo, inject it during pod installation
    base64 --decode $opts <<EOF | gunzip > src/PrivacyInfo.xcprivacy
      H4sICAAAAAAC/1ByaXZhY3lJbmZvLnhjcHJpdmFjeQC1kl9PwjAUxZ/Hp6h9Z1di/JsxAhskJAQXGQ8+
      Nt0VG7a1aRuw395OHUhE8UHflrNzzj2/pNHgpSrJBrURsu7TXnhOCdZcFqJe9ekyn3Rv6CDuRGfpfZI/
      ZmOiSmEsyZaj2TQhtAswVKpEgDRPSTabLnLiOwDGc0ros7XqDmC73YascYVcVo3RQKalQm3dzJd1fSAs
      bEH9mff2gzleLQS3cSeI1uji+SLTYsO4yzXja78ygkb2f59YaRC++BJZlsgtFimzLHcKzS7BtGYOvm1O
      ZcVEfdI+5ByNwWKYTY/U+4+gBQh+TrZBbzNW+wFHnQmzuJLaTUSJuajQWFapCD4SJ488IDNyDxV8mrm/
      m1z1rsPeYSnscaDl+RewhTMWq5GUtsH7Y7KLy8ntL8h2WqtE8PY0484rAb5xoDEDAAA=
    EOF

    # We are renaming openssl to openssl_grpc so that there is no conflict with openssl if it exists
    find . -type f \\( -path '*.h' -or -path '*.cc' -or -path '*.c' \\) -print0 | xargs -0 -L1 sed -E -i'.grpc_back' 's;#include <openssl/;#include <openssl_grpc/;g'

    # Include of boringssl_prefix_symbols.h does not follow Xcode import style. We add the package
    # name here so that Xcode knows where to find it.
    find . -type f \\( -path '*.h' -or -path '*.cc' -or -path '*.c' \\) -print0 | xargs -0 -L1 sed -E -i'.grpc_back' 's;#include <boringssl_prefix_symbols.h>;#include <openssl_grpc/boringssl_prefix_symbols.h>;g'
  END_OF_COMMAND
end
