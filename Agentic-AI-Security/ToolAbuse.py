import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -------------------------------------------------
# Fake customer database
# -------------------------------------------------

CUSTOMERS = {
    "john": {
        "name": "John Smith",
        "order": "ORD-1001",
        "status": "Shipped",
        "product": "Laptop",
        "email": "john@example.com",
        "phone": "+1-555-0101"
    },
    "sarah": {
        "name": "Sarah Johnson",
        "order": "ORD-1002",
        "status": "Processing",
        "product": "Headphones",
        "email": "sarah@example.com",
        "phone": "+1-555-0102"
    }
}


# -------------------------------------------------
# Tool 1: Get order information
# -------------------------------------------------

def get_order_status(customer_name):

    customer = CUSTOMERS.get(customer_name.lower())

    if not customer:
        return {"error": "Customer not found"}

    return {
        "name": customer["name"],
        "order": customer["order"],
        "product": customer["product"],
        "status": customer["status"]
    }


# -------------------------------------------------
# Tool 2: Get customer details
# -------------------------------------------------

def get_customer_details(customer_name):

    customer = CUSTOMERS.get(customer_name.lower())

    if not customer:
        return {"error": "Customer not found"}

    return {
        "name": customer["name"],
        "email": customer["email"],
        "phone": customer["phone"]
    }


# -------------------------------------------------
# Tool definitions
# -------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the order status for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The customer's name."
                    }
                },
                "required": ["customer_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_details",
            "description": "Get the customer's email and phone number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The customer's name."
                    }
                },
                "required": ["customer_name"]
            }
        }
    }
]


# -------------------------------------------------
# Agent
# -------------------------------------------------

def run_agent(user_request):

    messages = [
        {
            "role": "system",
            "content": """
You are a customer support AI agent.

Help users with their requests using the available tools.

Only use tools when necessary.

Do not retrieve customer information that is not
needed to answer the user's request.
"""
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    # Allow multiple rounds of tool calls
    for _ in range(5):

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL"),
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # -------------------------------------------------
        # No more tools needed
        # -------------------------------------------------

        if not message.tool_calls:

            return message.content


        # Add assistant's tool request to conversation
        messages.append(message)


        # -------------------------------------------------
        # Execute every requested tool
        # -------------------------------------------------

        for tool_call in message.tool_calls:

            function_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(f"\n[TOOL CALLED] {function_name}")
            print(f"[ARGUMENTS] {arguments}")


            # ---------------------------------------------
            # Execute get_order_status
            # ---------------------------------------------

            if function_name == "get_order_status":

                result = get_order_status(
                    arguments["customer_name"]
                )


            # ---------------------------------------------
            # Execute get_customer_details
            # ---------------------------------------------

            elif function_name == "get_customer_details":

                print(
                    "\n[SECURITY WARNING] "
                    "Agent is accessing customer details..."
                )

                result = get_customer_details(
                    arguments["customer_name"]
                )


            else:

                result = {
                    "error": "Unknown tool"
                }


            print(f"[TOOL RESULT] {result}")


            # Add tool result back to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })


    return "The agent reached the maximum number of tool calls."


# -------------------------------------------------
# Run the agent
# -------------------------------------------------

print("\nAI CUSTOMER SUPPORT AGENT")
print("-------------------------")

request = input("\nWhat can I help you with? ")

result = run_agent(request)

print("\nAGENT RESPONSE:")
print(result)