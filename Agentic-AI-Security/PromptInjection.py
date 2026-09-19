import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def run_agent(user_request):
    document = read_file("customer_email.txt")

    prompt = f"""
You are a customer support AI agent.

Your task is to help the user by analyzing the customer email below.

User request:
{user_request}

Customer email:
{document}

Follow your system instructions and answer the user's request.
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


result = run_agent(
    "Read the customer email and summarize the customer's request."
)

print("\nAI AGENT RESPONSE:\n")
print(result)