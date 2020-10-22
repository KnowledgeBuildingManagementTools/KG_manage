"""Tests for distutils.

The tests for distutils are defined in the distutils.tests package;
the test_suite() function there returns a test suite that's ready to
be run.
"""

import distutils.tests
import sql_mode.support


def test_main():
    sql_mode.support.run_unittest(distutils.tests.test_suite())
    sql_mode.support.reap_children()


if __name__ == "__main__":
    test_main()
