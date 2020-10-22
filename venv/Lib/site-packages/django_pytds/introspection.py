from django.db.backends import BaseDatabaseIntrospection
import pytds

class DatabaseIntrospection(BaseDatabaseIntrospection):
    def get_table_list(self, cursor):
        "Return a list of table and view names in the current database."
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' UNION SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS")
        return [row[0] for row in cursor.fetchall()]

    def _is_auto_field(self, cursor, table_name, column_name):
        """Check if a column is an identity column.

        See: http://msdn2.microsoft.com/en-us/library/ms174968.aspx
        """
        sql = "SELECT COLUMNPROPERTY(OBJECT_ID(N'%s'), N'%s', 'IsIdentity')" % \
            (table_name, column_name)

        cursor.execute(sql)
        return cursor.fetchone()[0]

    def get_table_description(self, cursor, table_name, identity_check=True):
        """Return a description of the table, with DB-API cursor.description interface.

        The 'auto_check' parameter has been added to the function argspec.
        If set to True, the function will check each of the table's fields for the
        IDENTITY property (the IDENTITY property is the MSSQL equivalent to an AutoField).

        When a field is found with an IDENTITY property, it is given a custom field number
        of SQL_AUTOFIELD, which maps to the 'AutoField' value in the DATA_TYPES_REVERSE dict.
        """
        cursor.execute("SELECT * FROM [%s] where 1=0" % (table_name))
        columns = cursor.native_description

        items = list()
        for column in columns:
            column = list(column) # Convert tuple to list
            if identity_check and self._is_auto_field(cursor, table_name, column[0]):
                column[1] = 'AUTO_FIELD_MARKER'
            items.append(column)
        return items

    def _name_to_index(self, cursor, table_name):
        """Return a dictionary of {field_name: field_index} for the given table.
        
        Indexes are 0-based.
        """
        return dict([(d[0], i) for i, d in enumerate(self.get_table_description(cursor, table_name, False))])

    def get_relations(self, cursor, table_name):
        source_field_dict = self._name_to_index(cursor, table_name)

        sql = """
select
    COLUMN_NAME = fk_cols.COLUMN_NAME,
    REFERENCED_TABLE_NAME = pk.TABLE_NAME,
    REFERENCED_COLUMN_NAME = pk_cols.COLUMN_NAME
from INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS ref_const
join INFORMATION_SCHEMA.TABLE_CONSTRAINTS fk
	on ref_const.CONSTRAINT_CATALOG = fk.CONSTRAINT_CATALOG
	and ref_const.CONSTRAINT_SCHEMA = fk.CONSTRAINT_SCHEMA
	and ref_const.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
	and fk.CONSTRAINT_TYPE = 'foreign key'

join INFORMATION_SCHEMA.TABLE_CONSTRAINTS pk
	on ref_const.UNIQUE_CONSTRAINT_CATALOG = pk.CONSTRAINT_CATALOG
	and ref_const.UNIQUE_CONSTRAINT_SCHEMA = pk.CONSTRAINT_SCHEMA
	and ref_const.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
	And pk.CONSTRAINT_TYPE = 'primary key'

join INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk_cols
	on ref_const.CONSTRAINT_NAME = fk_cols.CONSTRAINT_NAME

Join INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk_cols
	on pk.CONSTRAINT_NAME = pk_cols.CONSTRAINT_NAME
where
	fk.TABLE_NAME = %s"""

        cursor.execute(sql,[table_name])
        relations = cursor.fetchall()
        relation_map = dict()

        for source_column, target_table, target_column in relations:
            target_field_dict = self._name_to_index(cursor, target_table)
            target_index = target_field_dict[target_column]
            source_index = source_field_dict[source_column]

            relation_map[source_index] = (target_index, target_table)

        return relation_map

    def get_indexes(self, cursor, table_name):
    #    Returns a dictionary of fieldname -> infodict for the given table,
    #    where each infodict is in the format:
    #        {'primary_key': boolean representing whether it's the primary key,
    #         'unique': boolean representing whether it's a unique index}
        sql = """
select
	C.name as [column_name],
	IX.is_unique as [unique],
    IX.is_primary_key as [primary_key]
from
	sys.tables T
	join sys.index_columns IC on IC.object_id = T.object_id
	join sys.columns C on C.object_id = T.object_id and C.column_id = IC.column_id
	join sys.indexes Ix on Ix.object_id = T.object_id and Ix.index_id = IC.index_id
where
	T.name = %s
	and (Ix.is_unique=1 or Ix.is_primary_key=1)
    -- Omit multi-column keys
	and not exists (
		select *
		from sys.index_columns cols
		where
			cols.object_id = T.object_id
			and cols.index_id = IC.index_id
			and cols.key_ordinal > 1
	)
"""
        cursor.execute(sql,[table_name])
        constraints = cursor.fetchall()
        indexes = dict()

        for column_name, unique, primary_key in constraints:
            indexes[column_name.lower()] = {"primary_key":primary_key, "unique":unique}

        return indexes


    data_types_reverse = {
        'AUTO_FIELD_MARKER': 'AutoField',
        pytds.SYBBIT: 'BooleanField',
        pytds.XSYBCHAR: 'CharField',
        pytds.XSYBNCHAR: 'CharField',
        pytds.SYBDECIMAL: 'DecimalField',
        pytds.SYBNUMERIC: 'DecimalField',
        #pytds.adDBTimeStamp: 'DateTimeField',
        pytds.SYBREAL: 'FloatField',
        pytds.SYBFLT8: 'FloatField',
        pytds.SYBINT4: 'IntegerField',
        pytds.SYBINT8: 'BigIntegerField',
        pytds.SYBINT2: 'IntegerField',
        pytds.SYBINT1: 'IntegerField',
        pytds.XSYBVARCHAR: 'CharField',
        pytds.XSYBNVARCHAR: 'CharField',
        pytds.SYBTEXT: 'TextField',
        pytds.SYBNTEXT: 'TextField',
    }
