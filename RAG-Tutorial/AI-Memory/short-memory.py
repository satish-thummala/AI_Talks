import os
from dotenv import load_dotenv
from groq import Groq

# -------------------------------------------------
# Load Environment Variables
# -------------------------------------------------

load_dotenv()

# Initialize Groq client with API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant."
    }
]

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    # Add user's message to conversation history
    messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content

    print("AI:", assistant_reply)

    # Add AI's response to conversation history
    messages.append({
        "role": "assistant",
        "content": assistant_reply
    })