import os
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
        "product": "Laptop",
        "status": "Shipped",
        "email": "john@example.com",
        "phone": "+1-555-0101",
        "credit_card": "4111-1111-1111-1111"
    }
}


# -------------------------------------------------
# Get customer information
# -------------------------------------------------

def get_customer(customer_name):

    return CUSTOMERS.get(
        customer_name.lower()
    )


# -------------------------------------------------
# AI Agent
# -------------------------------------------------

def run_agent(user_request):

    customer = get_customer("john")

    # Only send the information needed
    # to answer the request
    safe_customer_data = {
        "name": customer["name"],
        "order": customer["order"],
        "product": customer["product"],
        "status": customer["status"]
    }

    print("\n[SECURE] Data being sent to the AI:")
    print(safe_customer_data)

    prompt = f"""
You are a customer support assistant.

Answer the user's question using the
customer information below.

User request:
{user_request}

Customer information:
{safe_customer_data}
"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You are a helpful customer support assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# -------------------------------------------------
# Run
# -------------------------------------------------

print("\nAI CUSTOMER SUPPORT AGENT")
print("-------------------------")

request = input("\nWhat can I help you with? ")

result = run_agent(request)

print("\nAGENT RESPONSE:")
print(result)