import os
import json
from dotenv import load_dotenv
from datetime import datetime
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MEMORY_FILE = "episodic_memory.json"


# -----------------------------------
# Load previous memories
# -----------------------------------

def load_memories():

    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return []


# -----------------------------------
# Save a new episode
# -----------------------------------

def save_episode(user_message, assistant_response):

    memories = load_memories()

    episode = {
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "assistant": assistant_response
    }

    memories.append(episode)

    with open(MEMORY_FILE, "w") as file:
        json.dump(memories, file, indent=4)


# -----------------------------------
# Find relevant past episodes
# -----------------------------------

def find_relevant_episodes(query):

    memories = load_memories()

    # Simple keyword matching for demonstration
    relevant = []

    query_words = set(query.lower().split())

    for memory in memories:

        text = (
            memory["user"] + " " +
            memory["assistant"]
        ).lower()

        if any(word in text for word in query_words):
            relevant.append(memory)

    return relevant[-3:]


# -----------------------------------
# Chat with episodic memory
# -----------------------------------

def chat():

    print("AI Assistant")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        # Retrieve relevant past experiences
        past_episodes = find_relevant_episodes(user_input)

        # Build memory context
        memory_context = ""

        for episode in past_episodes:

            memory_context += f"""
Date: {episode['timestamp']}
User: {episode['user']}
AI: {episode['assistant']}
"""

        prompt = f"""
You are a helpful AI assistant.

Here are some relevant experiences from previous
conversations:

{memory_context}

Use these past experiences when they are relevant.

Current user message:
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

        assistant_response = response.choices[0].message.content

        print("AI:", assistant_response)

        # Save this interaction as an episode
        save_episode(
            user_input,
            assistant_response
        )


# -----------------------------------
# Start application
# -----------------------------------

chat()