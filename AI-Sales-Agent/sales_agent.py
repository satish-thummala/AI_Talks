import json
import os

from groq import Groq
from dotenv import load_dotenv

from tools import (
    load_products,
    score_lead,
    save_lead
)


# Load environment variables
load_dotenv()


# Create GROQ client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


# --------------------------------------------------
# TOOL DEFINITIONS
# --------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "load_products",
            "description": "Get information about the company's products, features and pricing.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "score_lead",
            "description": "Score a sales lead and classify it as HOT, WARM or COLD.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Name of the company"
                    },
                    "employees": {
                        "type": "integer",
                        "description": "Number of employees in the company"
                    },
                    "interest": {
                        "type": "string",
                        "description": "What the customer is interested in"
                    }
                },
                "required": [
                    "company",
                    "employees",
                    "interest"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_lead",
            "description": "Save the processed sales lead into the CRM database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "email": {
                        "type": "string"
                    },
                    "company": {
                        "type": "string"
                    },
                    "lead_score": {
                        "type": "integer"
                    },
                    "lead_category": {
                        "type": "string"
                    },
                    "next_action": {
                        "type": "string"
                    }
                },
                "required": [
                    "name",
                    "email",
                    "company",
                    "lead_score",
                    "lead_category",
                    "next_action"
                ]
            }
        }
    }
]


# --------------------------------------------------
# TOOL EXECUTION
# --------------------------------------------------

def execute_tool(tool_name, arguments):

    if tool_name == "load_products":

        return load_products()

    elif tool_name == "score_lead":

        return score_lead(
            company=arguments["company"],
            employees=arguments["employees"],
            interest=arguments["interest"]
        )

    elif tool_name == "save_lead":

        save_lead(arguments)

        return {
            "status": "success",
            "message": "Lead saved successfully."
        }

    else:

        return {
            "error": f"Unknown tool: {tool_name}"
        }


# --------------------------------------------------
# AI SALES EMPLOYEE
# --------------------------------------------------

def process_lead(lead):

    system_prompt = """
You are an AI Sales Employee.

Your job is to process incoming sales leads.

You have access to tools that allow you to:

- Read company product information
- Score sales leads
- Save leads to the CRM

You should decide when to use these tools.

Your workflow should be:

1. Understand the lead.
2. Read the product information.
3. Score the lead.
4. Identify the best product.
5. Recommend the next sales action.
6. Write a personalized sales email.
7. Save the lead information.

Do not invent product features or pricing.

Once you have completed the workflow, provide a clear summary.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"""
Process this sales lead:

{json.dumps(lead, indent=2)}
"""
        }
    ]

    # --------------------------------------------------
    # FIRST AI REQUEST
    # --------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # --------------------------------------------------
    # TOOL CALLING LOOP
    # --------------------------------------------------

    while True:

        message = response.choices[0].message

        # Add assistant response to conversation
        messages.append(message)

        # If the AI doesn't request a tool,
        # we are finished.
        if not message.tool_calls:
            break

        # Execute every tool requested by the AI
        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"\nAI is using tool: {tool_name}"
            )

            print(
                f"Arguments: {arguments}"
            )

            # Execute the Python function
            result = execute_tool(
                tool_name,
                arguments
            )

            # Send the tool result back to the AI
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result)
                }
            )

        # Ask the AI what to do next
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

    return message.content