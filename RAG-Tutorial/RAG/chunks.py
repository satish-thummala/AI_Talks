from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Path to the PDF
pdf_path = "documents/Employee-Handbook.pdf"

print("=" * 60)
print("Loading PDF...")
print("=" * 60)

# Create the loader
loader = PyPDFLoader(pdf_path)

# Load the PDF
documents = loader.load()

print("\nPDF Loaded Successfully!")
print(f"Total Pages: {len(documents)}")

print("\n" + "=" * 60)
print("Splitting Documents into Chunks...")
print("=" * 60)

# Create the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

# Split the documents
chunks = text_splitter.split_documents(documents)

print(f"\nTotal Chunks Created: {len(chunks)}")

# Display the first 5 chunks
for i, chunk in enumerate(chunks[:5]):
    print("\n" + "=" * 60)
    print(f"Chunk {i + 1}")
    print("=" * 60)
    print(chunk.page_content)