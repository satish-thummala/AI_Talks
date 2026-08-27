import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Initialize clients
# -----------------------------

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB
chroma_client = chromadb.PersistentClient(path="./memory_db")

memory_collection = chroma_client.get_or_create_collection(
    name="user_memory"
)


# -----------------------------
# 2. Function to save memory
# -----------------------------

def save_memory(memory):

    embedding = embedding_model.encode(memory).tolist()

    memory_collection.add(
        documents=[memory],
        embeddings=[embedding],
        ids=[str(memory_collection.count())]
    )

    print("Memory saved:", memory)


# -----------------------------
# 3. Function to search memory
# -----------------------------

def search_memory(query, n_results=3):

    query_embedding = embedding_model.encode(query).tolist()

    results = memory_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0]


# -----------------------------
# 4. Save some user memories
# -----------------------------

save_memory(
    "The user loves Python programming."
)

save_memory(
    "The user is currently learning AI agents."
)

save_memory(
    "The user prefers practical hands-on AI tutorials."
)


# -----------------------------
# 5. Ask a question
# -----------------------------

query = "What programming language is the user interested in?"

memories = search_memory(query)

print("\nRelevant memories:")

for memory in memories:
    print("-", memory)


# -----------------------------
# 6. Give memories to the LLM
# -----------------------------

memory_text = "\n".join(memories)

prompt = f"""
You are a helpful AI assistant.

Here are some memories about the user:

{memory_text}

Answer the user's question using the relevant memories.

User question:
{query}
"""

response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\nAI:", response.choices[0].message.content)