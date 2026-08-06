from langchain_community.document_loaders import PyPDFLoader

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

print("\n" + "=" * 60)
print("Document Summary")
print("=" * 60)

for i, doc in enumerate(documents):
    print(f"\nPage {i + 1}")
    print("-" * 40)
    print(doc.page_content[:200]) 

print("\n" + "=" * 60)
print("Document Metadata")
print("=" * 60)

print(documents[0].metadata)