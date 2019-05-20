from sqlite3 import connect
from os import path


DB_FILENAME = "symbology.db"
DB_FILE = path.join("..", "storage", DB_FILENAME)


class Database:

    def __init__(self):
        # flag setup tables if database does not exist
        setup = False if path.isfile(DB_FILE) else True

        # connect to database
        self._con = connect(DB_FILE)
        self._con.row_factory = self._row_factory

        # setup database
        if setup:
            self.setup()

    @staticmethod
    def _row_factory(cursor, row):
        data = {}
        for idx, col in enumerate(cursor.description):
            data[col[0]] = row[idx]

        return data

    def setup(self):
        cursor = self._con.cursor()

        cursor.execute(
            f"""
                CREATE TABLE symbols (
                    alias text PRIMARY KEY,
                    symbol text,
                    created date
                )
            """
        )

        self._con.commit()

    def get_table_columns(self, table):
        cursor = self._con.cursor()
        cursor.execute(f"PRAGMA table_info({table});")

        recs = cursor.fetchall()

        return [rec.get("name") for rec in recs]

    def select(self, table, columns=None, filters=None):
        if columns and not isinstance(columns, list):
            raise TypeError("columns must be a list")

        if filters and not isinstance(filters, list):
            raise TypeError("filters must be a list")

        columns_to_query = ", ".join(columns) if columns else "*"
        query = f"SELECT {columns_to_query} FROM {table}"

        if filters:
            items = ["column", "operator", "value"]
            for i, filter in enumerate(filters):
                if not isinstance(filter, dict) or not all(item in items for item in filter.keys()):
                    raise TypeError("filter must be a dictionary and contain the keys column, operator and value")

                column = filter.get("column")
                operator = filter.get("operator")
                value = filter.get("value")

                clause = "WHERE" if i == 0 else "AND"
                condition = f"{clause} {column} {operator} '{value}'"

                query = f"{query}\n{condition}"

        cursor = self._con.cursor()
        cursor.execute(query)

        return cursor.fetchall()

    def insert(self, table, record):
        keys = record.keys()
        valid = all(k in self.get_table_columns(table) for k in keys)
        if not valid:
            invalid = list(set(keys) - set(self.get_table_columns(table)))
            raise ValueError("invalid key(s) supplied in record: {}".format(invalid))

        insert_columns = ", ".join(keys)

        values = [record.get(k) for k in keys]
        insert_values = ", ".join("?" * len(keys))

        cursor = self._con.cursor()
        cursor.execute(
            f"""
                INSERT INTO {table} ({insert_columns})
                VALUES({insert_values})
            """,
            values)

        self._con.commit()

    def __del__(self):
        self._con.close()

#
# if __name__ == "__main__":
#     from random import choice
#     from string import ascii_uppercase, digits
#
#     def _generate():
#         code = "".join(choice(ascii_uppercase + digits) for _ in range(7))
#         return f"SYM{code}"
#
#     # test = _generate()
#     # print(test)
#     # exit()
#
#     # TODO uppercase
#     alias = "ABC.JKL"
#
#     db = Database()
#
#     filters = [
#         {"column": "alias", "operator": "=", "value": alias}
#     ]
#     recs = db.select("symbols", "alias symbol".split(), filters=filters)
#
#     # symbol exists (return)
#     if recs:
#         print("exists", recs[0].get("symbol"))
#         exit()
#
#     # symbol does not exist (generate and return)
#     symbol = None
#     while True:
#         symbol = _generate()
#         filters = [
#             {"column": "symbol", "operator": "=", "value": symbol}
#         ]
#         recs = db.select("symbols", filters=filters)
#         if not recs:
#             break
#
#     db.insert("symbols", {"symbol": symbol, "alias": alias})
#
#     print("new", symbol)
#
#     test = None
