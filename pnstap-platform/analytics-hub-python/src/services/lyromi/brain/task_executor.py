from ..query_registry import QueryRegistry
from ..enterprise_formatter import EnterpriseFormatter

from ..tools.sql_executor import SQLExecutor
from ..tools.schema_loader import SchemaLoader
from ..tools.sql_generator import SQLGenerator


class TaskExecutor:

    @staticmethod
    def execute(
        task: str,
        question: str = "",
        params=None
    ):

        print("\n========== TASK EXECUTOR ==========")
        print("TASK:", task)

        # ---------------------------------------------------------
        # Parameters
        # ---------------------------------------------------------

        if params is None:
            params = ()

        print("PARAMS:", params)

        # ---------------------------------------------------------
        # Get registered query
        # ---------------------------------------------------------

        sql = QueryRegistry.get(task)

        print("FOUND QUERY:", sql is not None)

        # ---------------------------------------------------------
        # AI SQL fallback
        # ---------------------------------------------------------

        if sql is None:

            print("USING AI SQL GENERATOR")

            schema = SchemaLoader.load()

            sql = SQLGenerator.generate(
                question=question,
                schema=schema
            )

            query_params = None

        else:

            query_params = params

        # ---------------------------------------------------------
        # Display SQL
        # ---------------------------------------------------------

        print("\nSQL TO EXECUTE:\n")
        print(sql)

        if query_params:
            print("\nSQL PARAMETERS:")
            print(query_params)

        print("\n===============================\n")

        # ---------------------------------------------------------
        # Execute SQL
        # ---------------------------------------------------------

        raw_result = SQLExecutor.execute(
            sql,
            params=query_params
        )

        # ---------------------------------------------------------
        # Format result
        # ---------------------------------------------------------

        formatted = EnterpriseFormatter.format(
            task,
            raw_result
        )

        print("FORMATTED RESULT:")
        print(formatted)

        return formatted