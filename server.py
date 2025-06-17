# Import depdendencies
from mcp.server.fastmcp import FastMCP
import os
import clickhouse_connect
import json

# Server created
mcp = FastMCP("clickhouse_db")

def get_clickhouse_client():
    """Gets ClickHouse client from environment variables."""
    try:
        client = clickhouse_connect.get_client(
            host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
            port=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
            user=os.environ.get("CLICKHOUSE_USER", "default"),
            password=os.environ.get("CLICKHOUSE_PASSWORD", ""),
        )
        client.ping()
        return client
    except Exception as e:
        print(f"Failed to connect to ClickHouse: {e}")
        return None

@mcp.tool()
def execute_clickhouse_query(query: str) -> str:
    """
    Executes a read-only SQL query against the ClickHouse database and returns the result as a JSON string.
    Allowed queries: SELECT, SHOW, DESCRIBE.

    Args:
        query: The SQL query to execute.

    Returns:
        A JSON string representation of the query result, or an error message.
    """
    client = get_clickhouse_client()
    if not client:
        return "Error: ClickHouse connection failed."

    try:
        # A simple security measure to prevent modifications
        query_upper = query.strip().upper()
        if not (
            query_upper.startswith("SELECT")
            or query_upper.startswith("SHOW")
            or query_upper.startswith("DESCRIBE")
        ):
            return "Error: Only SELECT, SHOW, and DESCRIBE queries are allowed."

        result = client.query(query)
        if result.result_rows:
            # Get column names from the result
            column_names = result.column_names
            # Format result as a list of dictionaries
            formatted_result = [dict(zip(column_names, row)) for row in result.result_rows]
            return json.dumps(formatted_result, indent=2)
        else:
            return "[]"  # Return empty JSON array if no rows
    except Exception as e:
        return f"Error querying ClickHouse: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio") 