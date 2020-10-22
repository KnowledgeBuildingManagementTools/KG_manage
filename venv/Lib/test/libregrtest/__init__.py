# We import importlib *ASAP* in order to test #15386
import importlib

from sql_mode.libregrtest.cmdline import _parse_args, RESOURCE_NAMES
from sql_mode.libregrtest.main import main
