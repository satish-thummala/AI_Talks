import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq

from mcp import Client, StdioServerParameters


load_dotenv()


# -----------------------------
# Groq
# -----------------------------

groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


MODEL = os.getenv("GROQ_MODEL")


# -----------------------------
# MCP Server
# -----------------------------

server = StdioServerParameters(
    command=sys.executable,
    args=["mcp_server.py"]
)


# -----------------------------
# AI Agent
# -----------------------------

async def main():

    async with Client(server) as client:

        # Discover available MCP tools
        tools_result = await client.list_tools()

        print("\nAvailable MCP tools:")

        for tool in tools_result.tools:
            print(f"- {tool.name}: {tool.description}")

        # Convert MCP tools to Groq tool format
        groq_tools = []

        for tool in tools_result.tools:

            groq_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
            })

        # User request
        user_message = input(
            "\nAsk the AI Agent something about the surveys: "
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Surveys AI Agent. "
                    "Use the available tools when you need "
                    "information from the Surveys system. "
                    "Do not invent survey information."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Ask Groq what to do
        response = groq.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Add the assistant's response to the conversation
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in (assistant_message.tool_calls or [])
            ]
        })

        # Check whether the AI wants to call a tool
        if assistant_message.tool_calls:

            for tool_call in assistant_message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                print(f"\n[AI selected tool] {tool_name}")
                print(f"[Arguments] {arguments}")

                # MCP tool call
                result = await client.call_tool(
                    tool_name,
                    arguments
                )

                if result.is_error:
                    tool_result = "The tool returned an error."
                else:
                    tool_result = ""

                    for content in result.content:
                        if hasattr(content, "text"):
                            tool_result += content.text

                print("\n[MCP tool result]")
                print(tool_result)

                # Give the tool result back to the AI
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

            # Ask the AI to generate the final answer
            final_response = groq.chat.completions.create(
                model=MODEL,
                messages=messages
            )

            print("\n[AI Agent]")
            print(final_response.choices[0].message.content)

        else:

            print("\n[AI Agent]")
            print(assistant_message.content)


if __name__ == "__main__":
    asyncio.run(main())