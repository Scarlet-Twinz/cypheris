from .task_executor import TaskExecutor


class ToolRegistry:

    TOOLS = {

        "sql": TaskExecutor.execute,

        "report": TaskExecutor.execute,

        "summary": TaskExecutor.execute,

        "recommendation": TaskExecutor.execute,

    }

    @staticmethod
    def execute(tool_name: str, message: str):

        tool = ToolRegistry.TOOLS.get(tool_name)

        if tool is None:
            raise Exception(f"Unknown tool: {tool_name}")

        return tool(message)

    @staticmethod
    def list_tools():

        return list(ToolRegistry.TOOLS.keys())