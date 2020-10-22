# Tests that the crashers in the Lib/test/crashers directory actually
# do crash the interpreter as expected
#
# If a crasher is fixed, it should be moved elsewhere in the test suite to
# ensure it continues to work correctly.

import unittest
import glob
import os.path
import sql_mode.support
from sql_mode.support.script_helper import assert_python_failure

CRASHER_DIR = os.path.join(os.path.dirname(__file__), "crashers")
CRASHER_FILES = os.path.join(CRASHER_DIR, "*.py")

infinite_loops = ["infinite_loop_re.py", "nasty_eq_vs_dict.py"]

class CrasherTest(unittest.TestCase):

    @unittest.skip("these tests are too fragile")
    @sql_mode.support.cpython_only
    def test_crashers_crash(self):
        for fname in glob.glob(CRASHER_FILES):
            if os.path.basename(fname) in infinite_loops:
                continue
            # Some "crashers" only trigger an exception rather than a
            # segfault. Consider that an acceptable outcome.
            if sql_mode.support.verbose:
                print("Checking crasher:", fname)
            assert_python_failure(fname)


def tearDownModule():
    sql_mode.support.reap_children()

if __name__ == "__main__":
    unittest.main()
