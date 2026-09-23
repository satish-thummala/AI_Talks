import httpx
from mcp.server import MCPServer


# Your existing Surveys API
API_BASE_URL = "http://localhost:8000"


mcp = MCPServer(
    "Surveys MCP Server",
    instructions="Provides tools for interacting with the Surveys API."
)


@mcp.tool()
def list_surveys() -> str:
    """List all surveys available in the Surveys API."""

    response = httpx.get(
        f"{API_BASE_URL}/surveys",
        timeout=10.0
    )

    response.raise_for_status()

    return response.text


@mcp.tool()
def get_survey(survey_id: str) -> str:
    """Get a specific survey by its survey ID."""

    response = httpx.get(
        f"{API_BASE_URL}/surveys/{survey_id}",
        timeout=10.0
    )

    response.raise_for_status()

    return response.text


@mcp.tool()
def get_survey_responses(survey_id: str) -> str:
    """Get all responses submitted for a specific survey."""

    response = httpx.get(
        f"{API_BASE_URL}/surveys/{survey_id}/responses",
        timeout=10.0
    )

    response.raise_for_status()

    return response.text


if __name__ == "__main__":
    mcp.run()