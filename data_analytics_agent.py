import asyncio
import sys
import json
from typing import Any

# Agent imports
from beeai_framework.agents.types import AgentExecutionConfig
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage
from beeai_framework.emitter.emitter import Emitter, EventMeta
from beeai_framework.emitter.types import EmitterOptions
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.workflows.agent import AgentFactoryInput, AgentWorkflow
from beeai_framework.tools.code.python import PythonSandbox
from beeai_framework.tools.mcp import MCPTool

# MCP Client imports
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters


async def get_mcp_tools() -> list:
    """Initializes a connection to the MCP server using mcp_config.json."""
    try:
        with open("mcp_config.json", "r") as f:
            config = json.load(f)
        
        server_params = StdioServerParameters(
            command=config["command"], 
            args=config["args"],
            env=config.get("env")
        )
        
        async with stdio_client(server_params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            mcp_tool = await MCPTool.from_client(session, server_params)
            return [mcp_tool]
    except FileNotFoundError:
        print("Error: mcp_config.json not found.", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}", file=sys.stderr)
        return []

async def process_agent_events(event_data: dict[str, Any], event_meta: EventMeta) -> None:
    """Process and print agent events, focusing on the final response."""
    if event_meta.name == "error":
        print(f"Agent Error 🤖: {event_data['error']}", file=sys.stderr)
    elif event_meta.name == "update" and event_data["update"]["key"] == "response":
        print("\n--- Agent Final Response ---")
        print(event_data["update"]["parsedValue"])
        print("--------------------------")
    elif event_meta.name == "newToken" and "tool_code" in event_data["value"].tags:
        # Print the code the agent is about to execute
        print("\n--- Code to be Executed ---")
        print(event_data["value"].get_text_content())
        print("---------------------------")


async def observer(emitter: Emitter) -> None:
    emitter.on("*", process_agent_events, EmitterOptions(match_nested=True))


async def main() -> None:
    """Defines and runs the hybrid data analytics agent."""
    if len(sys.argv) < 2:
        print("Usage: python data_analytics_agent.py \"<Your question here>\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    # Initialize tools: SQL via MCP and Python via Sandbox
    mcp_tools = await get_mcp_tools()
    python_tool = PythonSandbox()
    all_tools = mcp_tools + [python_tool]

    if not all_tools:
        print("Error: No tools could be initialized. Exiting.", file=sys.stderr)
        return

    llm = ChatModel.from_name("ollama:granite3.1-dense:8b")

    instructions = """
    You are an expert data analyst. You have two types of tools at your disposal:
    1. `execute_clickhouse_query`: A tool to run SQL queries against a ClickHouse database. Use this for direct data retrieval, filtering, and simple aggregations.
    2. `python`: A Python code interpreter with `pandas` and `numpy`. Use this for complex calculations, multi-step data transformations, or when you need to combine data from multiple queries.

    To use the tools, you must write a `tool_code` block.

    Workflow:
    - First, understand the user's question.
    - Decide if the question is best answered with a direct SQL query or with Python code.
    - If SQL: use `execute_clickhouse_query` to get the data. The output will be a JSON string.
    - If Python: You can use the `execute_clickhouse_query` tool *inside* your Python code to fetch data into a pandas DataFrame.
      Example:
      ```python
      import json
      import pandas as pd
      # Notice the triple quotes for the SQL query string
      sql_result_json = execute_clickhouse_query(query='''SELECT * FROM events LIMIT 10''')
      data = json.loads(sql_result_json)
      df = pd.DataFrame(data)
      print(df)
      ```
    - Perform the necessary analysis and print the final answer.
    """

    workflow = AgentWorkflow(name="Hybrid Data Analyst")
    workflow.add_agent(
        agent=AgentFactoryInput(
            name="DataAnalystAgent",
            instructions=instructions,
            tools=all_tools,
            llm=llm,
            execution=AgentExecutionConfig(max_iterations=5)
        )
    )

    memory = UnconstrainedMemory()
    await memory.add(UserMessage(content=prompt))
    await workflow.run(messages=memory.messages).observe(observer)


if __name__ == "__main__":
    asyncio.run(main())
