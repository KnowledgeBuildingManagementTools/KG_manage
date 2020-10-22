# This dictionary maps Field objects to their associated Server Server column
# types, as strings. Column-type strings can contain format strings; they'll
# be interpolated against the values of Field.__dict__.
from django.conf import settings
from django.db.backends.creation import BaseDatabaseCreation, TEST_DATABASE_PREFIX
import sys

class DatabaseCreation(BaseDatabaseCreation):
    data_types = {
        'AutoField':                    'int IDENTITY (1, 1)',
        'BigAutoField':                 'bigint IDENTITY (1, 1)',
        'BigIntegerField':              'bigint',
        'BooleanField':                 'bit',
        'CharField':                    'nvarchar(%(max_length)s)',
        'CommaSeparatedIntegerField':   'nvarchar(%(max_length)s)',
        'DateField':                    'datetime',
        'DateTimeField':                'datetime',
        'DecimalField':                 'decimal(%(max_digits)s, %(decimal_places)s)',
        'FileField':                    'nvarchar(%(max_length)s)',
        'FilePathField':                'nvarchar(%(max_length)s)',
        'FloatField':                   'double precision',
        'IntegerField':                 'int',
        'IPAddressField':               'nvarchar(15)',
        'GenericIPAddressField':        'nvarchar(39)',
        'NullBooleanField':             'bit',
        'OneToOneField':                'int',
        'PositiveIntegerField':         'int CHECK ([%(column)s] >= 0)',
        'PositiveSmallIntegerField':    'smallint CHECK ([%(column)s] >= 0)',
        'SlugField':                    'nvarchar(%(max_length)s)',
        'SmallIntegerField':            'smallint',
        'TextField':                    'nvarchar(max)',
        'TimeField':                    'datetime',
    }

    def _create_master_connection(self):
        """
        Create a transactionless connection to 'master' database.
        """
        from base import DatabaseWrapper
        
        master_settings = self.connection.settings_dict
        if not master_settings['TEST_NAME']:
            master_settings['TEST_NAME'] = 'test_' + master_settings['NAME']
        master_settings['NAME'] = 'master'
        options = master_settings.setdefault('OPTIONS', {})
        options['autocommit'] = True
        return DatabaseWrapper(master_settings)

    def _create_test_db(self, verbosity=1, autoclobber=False):
        """
        Create the test databases using a connection to database 'master'.
        """
        test_database_name = self._test_database_name(settings)
        
        if not self._test_database_create(settings):
            if verbosity >= 1:
                print "Skipping Test DB creation"
            return test_database_name

        # clear any existing connections to the database
        old_wrapper = self.connection
        old_wrapper.close()

        # connect to master database
        self.connection = self._create_master_connection()
        
        try:
            super(DatabaseCreation, self)._create_test_db(verbosity, autoclobber)
        finally:
            # set thing back 
            self.connection = old_wrapper

        return test_database_name
        

    def _destroy_test_db(self, test_database_name, verbosity=1):
        """
        Drop the test databases using a connection to database 'master'.
        """
    
        if not self._test_database_create(settings):
            if verbosity >= 1:
                print "Skipping Test DB destruction"
            return

        old_wrapper = self.connection
        old_wrapper.close()
        self.connection = self._create_master_connection()
        
        try:
            super(DatabaseCreation, self)._destroy_test_db(test_database_name, verbosity)
        finally:
            self.connection = old_wrapper
            
        
    def _test_database_create(self, settings):
        """
        Check the settings to see if the test database should be created.
        """
        if self.connection.settings_dict.has_key('TEST_CREATE'):
            return self.connection.settings_dict.get('TEST_CREATE', True)
        if hasattr(settings, 'TEST_DATABASE_CREATE'):
            return settings.TEST_DATABASE_CREATE
        else:
            return True

    def _test_database_name(self, settings):
        """
        Get the test database name.
        """
        try:
            name = TEST_DATABASE_PREFIX + self.connection.settings_dict['NAME']
            if self.connection.settings_dict['TEST_NAME']:
                name = self.connection.settings_dict['TEST_NAME']
        except AttributeError:
            if hasattr(settings, 'TEST_DATABASE_NAME') and settings.TEST_DATABASE_NAME:
                name = settings.TEST_DATABASE_NAME
            else:
                name = TEST_DATABASE_PREFIX + settings.DATABASE_NAME
        return name
