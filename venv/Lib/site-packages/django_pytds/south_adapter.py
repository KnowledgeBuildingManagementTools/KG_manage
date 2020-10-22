from south.db.sql_server import pyodbc

class DatabaseOperations(pyodbc.DatabaseOperations):
    """
    django-mssql (sql_server.mssql) implementation of database operations.
    """
    backend_name = "pyodbc"

    def _fill_constraint_cache(self, db_name, table_name):

        schema = self._get_schema_name()
        ifsc_tables = ["CONSTRAINT_COLUMN_USAGE", "KEY_COLUMN_USAGE"]

        self._constraint_cache.setdefault(db_name, {})
        self._constraint_cache[db_name][table_name] = {}

        for ifsc_table in ifsc_tables:
            rows = self.execute("""
                SELECT kc.CONSTRAINT_NAME, kc.COLUMN_NAME, c.CONSTRAINT_TYPE
                FROM INFORMATION_SCHEMA.%s AS kc
                JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS c ON
                    kc.TABLE_SCHEMA = c.TABLE_SCHEMA AND
                    kc.TABLE_NAME = c.TABLE_NAME AND
                    kc.CONSTRAINT_NAME = c.CONSTRAINT_NAME
                WHERE
                    kc.TABLE_SCHEMA = %%s AND
                    kc.TABLE_NAME = %%s
            """ % ifsc_table, [schema, table_name])
            for constraint, column, kind in rows:
                self._constraint_cache[db_name][table_name].setdefault(column, set())
                self._constraint_cache[db_name][table_name][column].add((kind, constraint))
        return

    def _find_indexes_for_column(self, table_name, name):
        "Find the indexes that apply to a column, needed when deleting"

        sql = """
        SELECT si.name, si.id, sik.colid, sc.name
        FROM dbo.sysindexes si WITH (NOLOCK)
        INNER JOIN dbo.sysindexkeys sik WITH (NOLOCK)
            ON  sik.id = si.id
            AND sik.indid = si.indid
        INNER JOIN dbo.syscolumns sc WITH (NOLOCK)
            ON  si.id = sc.id
            AND sik.colid = sc.colid
        WHERE si.indid !=0
            AND si.id = OBJECT_ID('%s')
            AND sc.name = '%s'
        """
        idx = self.execute(sql % (table_name, name), [])
        return [i[0] for i in idx]
