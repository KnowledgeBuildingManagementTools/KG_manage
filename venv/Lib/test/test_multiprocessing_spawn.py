import unittest
import sql_mode._test_multiprocessing

from sql_mode import support

if support.PGO:
    raise unittest.SkipTest("test is not helpful for PGO")

sql_mode._test_multiprocessing.install_tests_in_module_dict(globals(), 'spawn')

if __name__ == '__main__':
    unittest.main()
