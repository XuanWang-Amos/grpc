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

import json
import os
import sys
import pkgutil
import unittest

import tests


class SanityTest(unittest.TestCase):
    maxDiff = 32768

    TEST_PKG_MODULE_NAME = "tests"
    TEST_PKG_PATH = "tests"

    def testTestsJsonUpToDate(self):
        """Autodiscovers all test suites and checks that tests.json is up to date"""
        loader = tests.Loader()
        loader.loadTestsFromNames([self.TEST_PKG_MODULE_NAME])
        test_suite_names = sorted(
            {
                test_case_class.id().rsplit(".", 1)[0]
                for test_case_class in tests._loader.iterate_suite_cases(
                    loader.suite
                )
            }
        )

        tests_json_string = ""
        if (os.name == "nt" or "darwin" in sys.platform) or self.TEST_PKG_PATH != "tests":
            tests_json_string = pkgutil.get_data(self.TEST_PKG_PATH, "tests.json")
        else:
            tests_json_string = pkgutil.get_data(self.TEST_PKG_PATH, "tests_native_linux.json")
        tests_json = json.loads(tests_json_string.decode())

        self.assertSequenceEqual(tests_json, test_suite_names)
        self.assertGreater(len(test_suite_names), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
