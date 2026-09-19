import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MEMORY_FILE = "agent_memory.json"


# -------------------------------------------------
# Memory functions
# -------------------------------------------------

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_memory(memory):

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)


def add_memory(memory_text):

    allowed_keywords = [
        "prefers",
        "preference",
        "likes",
        "dislikes",
        "preferred"
    ]

    text = memory_text.lower()

    if not any(
        keyword in text
        for keyword in allowed_keywords
    ):
        print("\n[MEMORY BLOCKED]")
        print("This information does not look like a")
        print("valid customer preference.")

        return

    memory = load_memory()

    memory.append({
        "memory": memory_text
    })

    save_memory(memory)

    print("\n[MEMORY SAVED]")


# -------------------------------------------------
# Agent
# -------------------------------------------------

def run_agent(user_request):

    memory = load_memory()

    memory_text = "\n".join(
        item["memory"]
        for item in memory
    )

    prompt = f"""
You are a helpful customer support AI agent.

Use the customer's previous memories to help
answer the current request.

Customer memories:
{memory_text}

Current user request:
{user_request}
"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
        messages=[
            {
                "role": "system",
                "content": """
You are a helpful customer support assistant.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# -------------------------------------------------
# Main program
# -------------------------------------------------

print("\nAI CUSTOMER SUPPORT AGENT")
print("-------------------------")

print("\nCurrent memory:")

memory = load_memory()

if not memory:
    print("No memories stored.")
else:
    for item in memory:
        print("-", item["memory"])


print("\n1. Add memory")
print("2. Ask the agent")

choice = input("\nChoose an option: ")


if choice == "1":

    memory_text = input(
        "\nWhat should the agent remember? "
    )

    add_memory(memory_text)

    print("\nMemory saved.")


elif choice == "2":

    request = input(
        "\nWhat can I help you with? "
    )

    result = run_agent(request)

    print("\nAGENT RESPONSE:")
    print(result)