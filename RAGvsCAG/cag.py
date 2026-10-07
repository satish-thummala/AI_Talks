import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------------
# 1. Load environment variables
# ---------------------------------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found. Please add your API key to the .env file."
    )


# ---------------------------------------------------------
# 2. Create Groq client
# ---------------------------------------------------------

client = Groq(api_key=api_key)


# ---------------------------------------------------------
# 3. Configuration
# ---------------------------------------------------------

KNOWLEDGE_DIR = Path("knowledge")

MODEL = os.getenv("GROQ_MODEL")


# ---------------------------------------------------------
# 4. Load knowledge base
# ---------------------------------------------------------

def load_knowledge():

    knowledge = []

    for file_path in sorted(
        KNOWLEDGE_DIR.glob("*.txt")
    ):

        text = file_path.read_text(
            encoding="utf-8"
        )

        knowledge.append(
            f"""
SOURCE: {file_path.name}

{text}
"""
        )

    return "\n".join(knowledge)


# ---------------------------------------------------------
# 5. Prepare the context
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("          PREPARING CAG CONTEXT")
print("=" * 60)

knowledge_context = load_knowledge()

if not knowledge_context.strip():

    raise ValueError(
        "No knowledge files found in the knowledge folder."
    )


print("\nKnowledge loaded into context:")

for file_path in sorted(
    KNOWLEDGE_DIR.glob("*.txt")
):

    print(f"  - {file_path.name}")


print("\nThe complete knowledge base is now ready.")

print("\nNo retriever will be used.")
print("No vector search will be performed.")
print("The knowledge will remain available in context.")


# ---------------------------------------------------------
# 6. Generate answer
# ---------------------------------------------------------

def generate_answer(question):

    prompt = f"""
You are a helpful AI assistant for TechNova.

You have been provided with TechNova's knowledge base below.

Answer the user's question using ONLY the information
contained in this knowledge base.

If the answer cannot be found in the knowledge base, say:

"I don't have enough information in the knowledge base to answer that."

Do not invent information.
Do not use outside knowledge.

================ KNOWLEDGE BASE ================

{knowledge_context}

================ END KNOWLEDGE BASE ================


USER QUESTION:

{question}


Provide a clear and concise answer.
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# 7. Run CAG pipeline
# ---------------------------------------------------------

def run_cag(question):

    print("\n" + "=" * 60)
    print("CAG PIPELINE")
    print("=" * 60)

    print("\n[1] User Question")
    print(question)

    print("\n[2] Using Prepared Context")

    print("TechNova knowledge base is already loaded.")

    print("\n[3] No Retrieval Required")

    print("There is no vector search or similarity search.")

    print("\n[4] Building Context-Augmented Prompt")

    print("User question + prepared knowledge")

    print("\n[5] Sending Context + Question to Groq")

    answer = generate_answer(question)

    print("\n[6] Final Answer")
    print("-" * 60)
    print(answer)
    print("-" * 60)


# ---------------------------------------------------------
# 8. Main program
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("          TECHNOVA CAG ASSISTANT")
    print("=" * 60)

    print("\nCAG works differently from RAG.")

    print(
        "\nThe knowledge base is loaded into the "
        "model's context before questions are asked."
    )

    print("\nType 'exit' to stop the program.")

    while True:

        question = input(
            "\nAsk a question: "
        ).strip()

        if question.lower() == "exit":

            print("\nGoodbye!")

            break

        if not question:

            continue

        run_cag(question)