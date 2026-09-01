import json
import os

from groq import Groq
from dotenv import load_dotenv

from tools import (
    load_products,
    score_lead,
    save_lead,
    send_email,
    schedule_meeting,
    update_crm
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
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send a personalized sales email to a lead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Customer email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body"
                    }
                },
                "required": [
                    "to",
                    "subject",
                    "body"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a sales meeting with a qualified lead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Customer name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer email"
                    },
                    "date": {
                        "type": "string",
                        "description": "Meeting date"
                    },
                    "time": {
                        "type": "string",
                        "description": "Meeting time"
                    }
                },
                "required": [
                    "name",
                    "email",
                    "date",
                    "time"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_crm",
            "description": "Update the CRM with the lead's current sales status and notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "company": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string",
                        "description": "Sales status such as HOT, WARM or COLD"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes about the lead"
                    }
                },
                "required": [
                    "name",
                    "company",
                    "status",
                    "notes"
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

    elif tool_name == "send_email":

        return send_email(
            to=arguments["to"],
            subject=arguments["subject"],
            body=arguments["body"]
        )

    elif tool_name == "schedule_meeting":

        return schedule_meeting(
            name=arguments["name"],
            email=arguments["email"],
            date=arguments["date"],
            time=arguments["time"]
        )

    elif tool_name == "update_crm":

        return update_crm(
            name=arguments["name"],
            company=arguments["company"],
            status=arguments["status"],
            notes=arguments["notes"]
        )

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

Your job is to process incoming sales leads and help move
qualified leads through the sales process.

You have access to tools that allow you to:

- Read company product information
- Score sales leads
- Save leads to the CRM
- Send sales emails
- Schedule sales meetings
- Update the CRM

Your job is to analyze each lead and decide which actions
are appropriate.

Follow this process:

1. Understand the lead.
2. Read the product information.
3. Score the lead.
4. Identify the best product.
5. Decide what action should be taken.

IMPORTANT DECISION RULES:

HOT LEAD:
- Send a personalized sales email.
- If the lead provides a preferred meeting date and time,
  schedule a sales meeting.
- Update the CRM as HOT.

WARM LEAD:
- Send a personalized sales email.
- Do not automatically schedule a meeting unless the lead
  specifically provides a preferred meeting time.
- Update the CRM as WARM.

COLD LEAD:
- Do not schedule a meeting.
- Do not send a sales email.
- Save the lead for future follow-up.
- Update the CRM as COLD.

Do not use tools unnecessarily.

Do not invent customer information.

Do not invent meeting dates or times.

Do not invent product features or pricing.

After completing the necessary actions, provide a concise
summary of what you decided and which actions you performed.
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