import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
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
# 3. Load embedding model
# ---------------------------------------------------------

print("\nLoading embedding model...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ---------------------------------------------------------
# 4. Load knowledge base
# ---------------------------------------------------------

KNOWLEDGE_DIR = Path("knowledge")


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):

        text = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "source": file_path.name,
                "text": text
            }
        )

    return documents


documents = load_documents()


if not documents:
    raise ValueError(
        "No documents found in the knowledge folder."
    )


# ---------------------------------------------------------
# 5. Split documents into chunks
# ---------------------------------------------------------

def create_chunks(text, chunk_size=500):

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks


chunks = []

for document in documents:

    document_chunks = create_chunks(
        document["text"]
    )

    for chunk in document_chunks:

        chunks.append(
            {
                "source": document["source"],
                "text": chunk
            }
        )


# ---------------------------------------------------------
# 6. Create embeddings
# ---------------------------------------------------------

print("Creating embeddings...")

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_model.encode(
    texts,
    convert_to_numpy=True
)


# ---------------------------------------------------------
# 7. Normalize embeddings
# ---------------------------------------------------------

def normalize(vectors):

    norms = np.linalg.norm(
        vectors,
        axis=1,
        keepdims=True
    )

    return vectors / norms


embeddings = normalize(embeddings)


# ---------------------------------------------------------
# 8. Retrieve relevant chunks
# ---------------------------------------------------------

def retrieve(question, top_k=3):

    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    )

    question_embedding = normalize(
        question_embedding
    )[0]

    similarities = embeddings @ question_embedding

    top_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    results = []

    for index in top_indices:

        results.append(
            {
                "source": chunks[index]["source"],
                "text": chunks[index]["text"],
                "score": float(similarities[index])
            }
        )

    return results


# ---------------------------------------------------------
# 9. Generate answer with Groq
# ---------------------------------------------------------

def generate_answer(question, retrieved_chunks):

    context = "\n\n".join(
        [
            f"Source: {chunk['source']}\n"
            f"{chunk['text']}"
            for chunk in retrieved_chunks
        ]
    )

    prompt = f"""
You are a helpful AI assistant for TechNova.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the context, say:

"I don't have enough information in the knowledge base to answer that."

Do not invent or assume information.

Context:
----------------
{context}
----------------

User Question:
{question}

Answer clearly and concisely.
"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL"),
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
# 10. Run the RAG pipeline
# ---------------------------------------------------------

def run_rag(question):

    print("\n" + "=" * 60)
    print("RAG PIPELINE")
    print("=" * 60)

    print("\n[1] User Question")
    print(question)

    print("\n[2] Searching Knowledge Base...")

    retrieved_chunks = retrieve(
        question,
        top_k=3
    )

    print("\n[3] Retrieved Context")

    for i, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        print(f"\n--- Result {i} ---")
        print(f"Source: {chunk['source']}")
        print(f"Similarity: {chunk['score']:.4f}")
        print(chunk["text"])

    print("\n[4] Building Augmented Prompt...")

    print("\n[5] Sending Context + Question to Groq...")

    answer = generate_answer(
        question,
        retrieved_chunks
    )

    print("\n[6] Final Answer")
    print("-" * 60)
    print(answer)
    print("-" * 60)


# ---------------------------------------------------------
# 11. Main program
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("          TECHNOVA RAG ASSISTANT")
    print("=" * 60)

    print("\nKnowledge base loaded:")
    
    for document in documents:
        print(f"  - {document['source']}")

    print("\nType 'exit' to stop the program.")

    while True:

        question = input("\nAsk a question: ").strip()

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        if not question:
            continue

        run_rag(question)