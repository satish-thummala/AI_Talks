from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load PDF
loader = PyPDFLoader("documents/Employee-Handbook.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages.")

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks.")

print("\nCreating embedding model...")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")

print("\nCreating Chroma Vector Database...")

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="./chroma_db"
)

print("Vector Database created successfully!")

print(f"\nStored {len(chunks)} document chunks.")


print("\n" + "=" * 60)
print("Similarity Search")
print("=" * 60)

query = "How many annual leave days do employees receive?"

results = vector_db.similarity_search(query, k=3)

print(f"\nQuestion: {query}")

print("\nTop 3 Matching Chunks:\n")

for i, doc in enumerate(results, start=1):
    print("=" * 60)
    print(f"Result {i}")
    print("=" * 60)
    print(doc.page_content)
    print()