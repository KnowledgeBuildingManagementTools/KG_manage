# Convenience test module to run all of the XML-related tests in the
# standard library.

import sys
import sql_mode.support

sql_mode.support.verbose = 0

def runtest(name):
    __import__(name)
    module = sys.modules[name]
    if hasattr(module, "test_main"):
        module.test_main()

runtest("test.test_minidom")
runtest("test.test_pyexpat")
runtest("test.test_sax")
runtest("test.test_xml_dom_minicompat")
runtest("test.test_xml_etree")
runtest("test.test_xml_etree_c")
runtest("test.test_xmlrpc")
