import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env file")

client = Groq(api_key=api_key)

# Select the language model
MODEL_NAME = os.getenv("GROQ_MODEL")


def ask_groq(prompt):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# Test Groq connection
if __name__ == "__main__":
    result = ask_groq(
        "Explain what an SQL database is in two sentences."
    )

    print("\nGroq Response:\n")
    print(result)
