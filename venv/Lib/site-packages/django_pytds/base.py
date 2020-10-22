"""Microsoft SQL Server database backend for Django."""
import sys

from django.db import utils
from django.conf import settings
from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseValidation, BaseDatabaseClient
from django.db.backends.signals import connection_created
try:
    from django.utils.timezone import utc
except:
    pass

import pytds as Database

from introspection import DatabaseIntrospection
from creation import DatabaseCreation
from operations import DatabaseOperations

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

class DatabaseFeatures(BaseDatabaseFeatures):
    uses_custom_query_class = True
    has_bulk_insert = False
    
    supports_timezones = False
    supports_sequence_reset = False
    
    can_return_id_from_insert = True
    
    supports_regex_backreferencing = False
    
    # Disable test modeltests.lookup.tests.LookupTests.test_lookup_date_as_str
    supports_date_lookup_using_string = False
    
    supports_tablespaces = True


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'microsoft'
    
    operators = {
        "exact": "= %s",
        "iexact": "LIKE %s ESCAPE '\\'",
        "contains": "LIKE %s ESCAPE '\\'",
        "icontains": "LIKE %s ESCAPE '\\'",
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s ESCAPE '\\'",
        "endswith": "LIKE %s ESCAPE '\\'",
        "istartswith": "LIKE %s ESCAPE '\\'",
        "iendswith": "LIKE %s ESCAPE '\\'",
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        
        try:
            # django < 1.3
            self.features = DatabaseFeatures()
        except TypeError:
            # django >= 1.3
            self.features = DatabaseFeatures(self)

        try:
            self.ops = DatabaseOperations()
        except TypeError:
            self.ops = DatabaseOperations(self)
        
        self.client = BaseDatabaseClient(self)
        self.creation = DatabaseCreation(self) 
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)

        try:
            self.command_timeout = int(self.settings_dict.get('COMMAND_TIMEOUT', 30))
        except ValueError:
            self.command_timeout = 30
        
        try:
            options = self.settings_dict.get('OPTIONS', {})
            self.cast_avg_to_float = not bool(options.get('disable_avg_cast', False))
            self.autocommit = bool(options.get('autocommit', False))
        except ValueError:
            self.cast_avg_to_float = False

    def _cursor(self):
        if self.connection is None:
            """Connect to the database"""
            options = self.settings_dict.get('OPTIONS', {})
            self.connection = Database.connect(
                server=self.settings_dict['HOST'],
                database=self.settings_dict['NAME'],
                user=self.settings_dict['USER'],
                password=self.settings_dict['PASSWORD'],
                timeout=self.command_timeout,
                autocommit=self.autocommit,
                use_mars=options.get('use_mars', False),
                load_balancer=options.get('load_balancer', None),
                use_tz=utc if settings.USE_TZ else None,
            )
            # The OUTPUT clause is supported in 2005+ sql servers
            self.features.can_return_id_from_insert = self.connection.tds_version >= Database.TDS72
            connection_created.send(sender=self.__class__, connection=self)
        return CursorWrapper(self.connection.cursor())

    def disable_constraint_checking(self):
        """
        Turn off constraint checking for every table
        """
        if self.connection:
            cursor = self.connection.cursor()
        else:
            cursor = self._cursor()
        cursor.execute('EXEC sp_MSforeachtable "ALTER TABLE ? NOCHECK CONSTRAINT all"')

    def enable_constraint_checking(self):
        """
        Turn on constraint checking for every table
        """
        if self.connection:
            cursor = self.connection.cursor()
        else:
            cursor = self._cursor()
        cursor.execute('EXEC sp_MSforeachtable "ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all"')

    def check_constraints(self, table_names=None):
        """
        Check the table constraints.
        """
        if self.connection:
            cursor = self.connection.cursor()
        else:
            cursor = self._cursor()
        if not table_names:
            cursor.execute('DBCC CHECKCONSTRAINTS')
        else:
            qn = self.ops.quote_name
            for name in table_names:
                cursor.execute('DBCC CHECKCONSTRAINTS({0})'.format(
                    qn(name)
                ))


class CursorWrapper(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cursor.close()

    def execute(self, sql, params = ()):
        try:
            return self.cursor.execute(sql, params)
        except Database.IntegrityError, e:
            if not self.cursor.connection.mars_enabled:
                self.cursor.cancel()
            raise utils.IntegrityError, utils.IntegrityError(*tuple(e)), sys.exc_info()[2]
        except Database.DatabaseError, e:
            if not self.cursor.connection.mars_enabled:
                self.cursor.cancel()
            raise utils.DatabaseError, utils.DatabaseError(*tuple(e)), sys.exc_info()[2]
        except Database.Error:
            if not self.cursor.connection.mars_enabled:
                self.cursor.cancel()
            raise

    def executemany(self, sql, params):
        try:
            return self.cursor.executemany(sql, params)
        except Database.IntegrityError, e:
            raise utils.IntegrityError, utils.IntegrityError(*tuple(e)), sys.exc_info()[2]
        except Database.DatabaseError, e:
            raise utils.DatabaseError, utils.DatabaseError(*tuple(e)), sys.exc_info()[2]

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)
