import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

# -------------------------------------------------
# Load Environment Variables
# -------------------------------------------------

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# -------------------------------------------------
# Load PDF
# -------------------------------------------------

pdf_path = "documents/Employee-Handbook.pdf"

print("=" * 60)
print("Loading PDF...")
print("=" * 60)

loader = PyPDFLoader(pdf_path)
documents = loader.load()

print(f"PDF Loaded Successfully!")
print(f"Total Pages: {len(documents)}")

# -------------------------------------------------
# Split into Chunks
# -------------------------------------------------

print("\n" + "=" * 60)
print("Splitting Documents into Chunks...")
print("=" * 60)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents)

print(f"Total Chunks Created: {len(chunks)}")

# -------------------------------------------------
# Create Embeddings
# -------------------------------------------------

print("\n" + "=" * 60)
print("Loading Embedding Model...")
print("=" * 60)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding Model Loaded Successfully!")

# -------------------------------------------------
# Create ChromaDB
# -------------------------------------------------

print("\n" + "=" * 60)
print("Creating Chroma Vector Database...")
print("=" * 60)

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)

print("Vector Database Created Successfully!")

# -------------------------------------------------
# Similarity Search
# -------------------------------------------------

print("\n" + "=" * 60)
print("Similarity Search")
print("=" * 60)

query = "How many annual leave days do employees receive?"

results = vector_db.similarity_search(query, k=3)

print(f"\nQuestion:\n{query}")

print("\nTop 3 Matching Chunks:\n")

for i, doc in enumerate(results, start=1):
    print("=" * 60)
    print(f"Result {i}")
    print("=" * 60)
    print(doc.page_content)
    print()

# -------------------------------------------------
# Create Groq LLM
# -------------------------------------------------

print("\n" + "=" * 60)
print("Connecting to Groq...")
print("=" * 60)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=groq_api_key
)

# -------------------------------------------------
# Prepare Context
# -------------------------------------------------

context = "\n\n".join(
    [doc.page_content for doc in results]
)

# -------------------------------------------------
# Prompt
# -------------------------------------------------

prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the information provided in the context below.

If the answer is not present in the context, simply reply:
"I couldn't find that information in the provided document."

Context:
{context}

Question:
{query}

Answer:
"""

# -------------------------------------------------
# Generate Final Answer
# -------------------------------------------------

print("\n" + "=" * 60)
print("Generating Final Answer...")
print("=" * 60)

response = llm.invoke(prompt)

print("\nFinal Answer:\n")
print(response.content)