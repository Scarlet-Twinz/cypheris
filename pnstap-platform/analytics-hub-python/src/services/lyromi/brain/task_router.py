from ..query_registry import QueryRegistry
from ..enterprise_formatter import EnterpriseFormatter

from ..tools.sql_executor import SQLExecutor
from ..tools.schema_loader import SchemaLoader
from ..tools.sql_generator import SQLGenerator


class TaskExecutor:

    @staticmethod
    def execute(task: str, question: str):

        print("\n========== TASK EXECUTOR ==========")
        print("TASK:", task)

        sql = QueryRegistry.get(task)

        print("FOUND QUERY:", sql is not None)

        # -----------------------------
        # AI SQL fallback
        # -----------------------------
        if sql is None:

            print("Using AI SQL Generator...")

            schema = SchemaLoader.load()

            sql = SQLGenerator.generate(
                question=question,
                schema=schema
            )

        print("\nSQL TO EXECUTE:\n")
        print(sql)
        print("\n===============================\n")

        raw_result = SQLExecutor.execute(sql)

        formatted = EnterpriseFormatter.format(
            task,
            raw_result
        )

        print("FORMATTED RESULT:")
        print(formatted)

        return formatted