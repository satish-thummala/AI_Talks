
"""Groq-powered AI agent for analyzing the local Excel sales workbook."""

import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from excel_tools import (
    get_order_status_summary,
    get_product_performance,
    get_region_performance,
    get_sales_overview,
)

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOOL_ROUNDS = 5

SYSTEM_PROMPT = """You are an AI sales analyst working with a local Excel workbook.
Use the available tools to answer questions about the workbook accurately.
Never invent figures. Base numerical claims on tool results, and explain currency
amounts in the same units used by the workbook. You may call more than one tool
when needed. If the data does not answer a question, say so clearly. Do not claim
to have modified the workbook; this version of the agent only reads and analyzes it.
Give concise, practical business insights and distinguish facts from suggestions."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_overview",
            "description": (
                "Get headline sales metrics, total units, revenue, average order "
                "revenue, and order status counts."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_performance",
            "description": (
                "Rank products by revenue. Use lowest=true to find the "
                "lowest-revenue products, or lowest=false for the highest-revenue products."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "integer",
                        "description": "Number of products to return, from 1 to 20.",
                    },
                    "lowest": {
                        "type": "boolean",
                        "description": (
                            "True for lowest revenue first; false for highest revenue first."
                        ),
                    },
                },
                "required": ["top_n", "lowest"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_region_performance",
            "description": (
                "Compare each region by revenue, revenue share, units sold, and order count."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status_summary",
            "description": "Summarize order counts and revenue grouped by order status.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Execute only explicitly allowed, locally defined tools."""
    if name == "get_sales_overview":
        return get_sales_overview()

    if name == "get_product_performance":
        top_n = arguments.get("top_n", 3)
        lowest = arguments.get("lowest", False)

        if not isinstance(top_n, int) or isinstance(top_n, bool):
            raise ValueError("top_n must be an integer.")
        if not isinstance(lowest, bool):
            raise ValueError("lowest must be true or false.")

        return get_product_performance(top_n=top_n, lowest=lowest)

    if name == "get_region_performance":
        return get_region_performance()

    if name == "get_order_status_summary":
        return get_order_status_summary()

    raise ValueError(f"Tool is not allowed: {name}")


def ask_agent(client: Groq, question: str) -> str:
    """Ask Groq a question and run tool calls requested by the model."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_completion_tokens=1200,
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        if not tool_calls:
            return assistant_message.content or "The model returned an empty response."

        # Keep the assistant's tool-call message before adding tool results.
        messages.append(assistant_message.model_dump(exclude_none=True))

        for tool_call in tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments or "{}")
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments must be a JSON object.")

                print(f"\n[Agent selected tool: {tool_name}]")
                print(f"[Arguments: {json.dumps(arguments)}]")

                result = execute_tool(tool_name, arguments)
                tool_result = {"ok": True, "result": result}

            except Exception as exc:
                # Return a controlled error; never execute arbitrary model-generated code.
                tool_result = {"ok": False, "error": str(exc)}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                        default=str,
                    ),
                }
            )

    return (
        "I reached the tool-call limit before completing the analysis. "
        "Please try a more focused question."
    )


def main() -> None:
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit(
            "GROQ_API_KEY is missing. Add it to a .env file in this project folder."
        )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    print("AI Excel Sales Analyst — Groq connected")
    print(f"Model: {MODEL_NAME}")
    print(
        "Ask about sales, products, regions, or order statuses. "
        "Type 'exit' to quit.\n"
    )

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            answer = ask_agent(client, question)
            print(f"\nAI Agent: {answer}\n")
        except Exception as exc:
            print(f"\nSomething went wrong: {exc}")
            print(
                "Check your API key, model availability, internet connection, "
                "and Groq usage limits.\n"
            )


if __name__ == "__main__":
    main()
