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

print("\nSample Chunk:\n")
print(chunks[5].page_content)

print("\nEmbedding Dimension:")
print(len(embedding_model.embed_query(chunks[5].page_content)))