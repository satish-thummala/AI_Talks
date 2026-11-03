
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Read configuration
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

if not model:
    raise ValueError("GROQ_MODEL is missing from .env")

# Initialize Groq client
client = Groq(api_key=api_key)


def ask_groq(prompt):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    result = ask_groq(
        "Explain what an AI research agent does in two sentences."
    )

    print("\nGroq Response:\n")
    print(result)
