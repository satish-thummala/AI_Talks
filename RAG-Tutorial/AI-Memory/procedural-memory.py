import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MEMORY_FILE = "procedural_memory.json"


# -----------------------------------
# Load procedural memories
# -----------------------------------

def load_procedures():

    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return []


# -----------------------------------
# Save a new procedure
# -----------------------------------

def save_procedure(procedure):

    procedures = load_procedures()

    if procedure not in procedures:
        procedures.append(procedure)

    with open(MEMORY_FILE, "w") as file:
        json.dump(procedures, file, indent=4)

    print("Procedure saved.")


# -----------------------------------
# Ask the AI to extract a procedure
# -----------------------------------

def learn_procedure(user_input):

    prompt = f"""
Analyze the user's message.

If the user is telling you how they want
a task to be performed in the future,
extract that instruction.

Return ONLY the instruction.
If there is no reusable instruction,
return NONE.

User message:
{user_input}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    procedure = response.choices[0].message.content.strip()

    if procedure != "NONE":
        save_procedure(procedure)


# -----------------------------------
# Generate response using procedures
# -----------------------------------

def generate_response(user_input):

    procedures = load_procedures()

    procedure_context = "\n".join(
        f"- {procedure}"
        for procedure in procedures
    )

    prompt = f"""
You are a helpful AI assistant.

Follow these instructions when performing tasks:

{procedure_context}

User request:
{user_input}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------------------
# Chat
# -----------------------------------

def chat():

    print("AI Assistant")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        # First learn whether this message
        # contains a reusable procedure
        learn_procedure(user_input)

        # Then generate the response
        answer = generate_response(user_input)

        print("\nAI:", answer)
        print()


chat()