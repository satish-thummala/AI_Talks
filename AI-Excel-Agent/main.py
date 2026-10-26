
"""AI Excel Sales Analyst using Groq and local Python tools."""

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
    create_ai_report,
)

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_TOOL_ROUNDS = 6

SYSTEM_PROMPT = """
You are an AI sales analyst working with a local Excel sales workbook.

Use the available Python tools to answer questions accurately.
Never invent numerical results. Use the tool results as your source of truth.

When asked to create or generate an Excel report:
1. Gather relevant sales information using the analysis tools.
2. Summarize the key findings using actual tool results.
3. Provide practical recommendations supported by those findings.
4. Call create_ai_report with a summary and a list of recommendations.
5. Confirm the report was created only if the tool returns success.

The report is saved to the existing workbook in a worksheet called AIReport.
Do not claim to have modified the workbook unless the report tool succeeds.

Do not execute arbitrary Python code or access tools that are not provided.
Keep your final answers clear, concise, and useful for a business user.
Recommendations should be presented as suggestions, not proven causes.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_overview",
            "description": (
                "Get headline sales metrics, total units, revenue, average "
                "order revenue, and order status counts."
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
                "Rank products by revenue. Use lowest=true for the lowest "
                "revenue products, or lowest=false for the highest revenue products."
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
                        "description": "True for lowest revenue first.",
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
                "Compare regions by revenue, revenue share, units sold, "
                "and order count."
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
            "description": "Summarize order counts and revenue by order status.",
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
            "name": "create_ai_report",
            "description": (
                "Create or replace the AIReport worksheet in the sales workbook. "
                "Call this after collecting the relevant sales results and preparing "
                "a factual summary and practical recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": (
                            "A concise report summary based on the actual tool results."
                        ),
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "A list of practical, evidence-based recommendations."
                        ),
                    },
                },
                "required": ["summary", "recommendations"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Execute only the Python tools explicitly allowed for this agent."""

    if name == "get_sales_overview":
        return get_sales_overview()

    if name == "get_product_performance":
        top_n = arguments.get("top_n", 3)
        lowest = arguments.get("lowest", False)

        if (
            not isinstance(top_n, int)
            or isinstance(top_n, bool)
            or not 1 <= top_n <= 20
        ):
            raise ValueError("top_n must be an integer between 1 and 20.")

        if not isinstance(lowest, bool):
            raise ValueError("lowest must be true or false.")

        return get_product_performance(top_n=top_n, lowest=lowest)

    if name == "get_region_performance":
        return get_region_performance()

    if name == "get_order_status_summary":
        return get_order_status_summary()

    if name == "create_ai_report":
        summary = arguments.get("summary")
        recommendations = arguments.get("recommendations")

        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("The report summary must be a non-empty string.")

        if (
            not isinstance(recommendations, list)
            or not all(
                isinstance(item, str) and item.strip()
                for item in recommendations
            )
        ):
            raise ValueError(
                "Recommendations must be a list of non-empty strings."
            )

        # The existing function writes the report into the Excel workbook.
        create_ai_report(
            summary=summary.strip(),
            recommendations=recommendations,
        )

        return {
            "success": True,
            "message": "The AIReport worksheet was created or updated successfully.",
            "worksheet": "AIReport",
        }

    raise ValueError(f"Tool is not allowed: {name}")


def ask_agent(client: Groq, question: str) -> str:
    """Send a question to Groq and process any requested tool calls."""

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
            max_completion_tokens=1500,
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        if not tool_calls:
            return (
                assistant_message.content
                or "The model returned an empty response."
            )

        # Preserve the assistant message so the API can match tool results
        # to the corresponding tool-call IDs.
        messages.append(assistant_message.model_dump(exclude_none=True))

        for tool_call in tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )

                if not isinstance(arguments, dict):
                    raise ValueError(
                        "Tool arguments must be a JSON object."
                    )

                print(f"\n[Agent selected tool: {tool_name}]")
                print(f"[Arguments: {json.dumps(arguments)}]")

                result = execute_tool(tool_name, arguments)
                tool_result = {
                    "ok": True,
                    "result": result,
                }

                if tool_name == "create_ai_report":
                    print("[Excel report created successfully.]")

            except Exception as exc:
                print(f"[Tool error: {tool_name}: {exc}]")
                tool_result = {
                    "ok": False,
                    "error": str(exc),
                }

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
        "The agent reached its tool-call limit before completing the request. "
        "Please try a more focused question."
    )


def main() -> None:
    """Start the interactive AI Excel agent."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise SystemExit(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    client = Groq(api_key=api_key)

    print("=" * 55)
    print("       AI Excel Sales Analyst")
    print("=" * 55)
    print(f"Model: {MODEL_NAME}")
    print("Ask about sales, products, regions, or order statuses.")
    print("Ask the agent to create an Excel report when needed.")
    print("Type 'exit' to quit.\n")

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
