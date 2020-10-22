"""
TZ helper functions backported from Django 1.4. This module should only 
get loaded if django.utils.timezone doesn't exist.
"""
from datetime import timedelta, tzinfo

try:
    import pytz
except ImportError:
    pytz = None


__all__ = [
    'utc', 'is_aware'
]

# UTC and local time zones

ZERO = timedelta(0)

class UTC(tzinfo):
    """
    UTC implementation taken from Python's docs.

    Used only when pytz isn't available.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = pytz.utc if pytz else UTC()
"""UTC time zone as a tzinfo instance."""


def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None
