from .database_tool import DatabaseTool


class SchemaLoader:

    @staticmethod
    def load():

        sql = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position;
        """

        rows = DatabaseTool.execute(sql)

        if not rows:
            return ""

        schema = {}

        for row in rows:

            table = row["table_name"]

            column = row["column_name"]

            datatype = row["data_type"]

            if table not in schema:
                schema[table] = []

            schema[table].append(
                f"{column} ({datatype})"
            )

        output = []

        for table, columns in schema.items():

            output.append(f"Table: {table}")

            for column in columns:

                output.append(f"  - {column}")

            output.append("")

        return "\n".join(output)