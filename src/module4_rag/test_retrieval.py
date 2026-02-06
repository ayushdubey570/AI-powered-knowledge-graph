import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURATION ---
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def test_semantic_search():
    print("⏳ Loading Embedding Model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("🔄 Connecting to Vector Index...")
    
    # Connect to the Index you just built
    vector_store = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        index_name="ticket_description_vector",
        node_label="Ticket",
        text_node_properties=["description"],
        embedding_node_property="embedding",
    )

    # --- THE TEST ---
    query = "My device is too hot"
    print(f"\n🔎 Testing Query: '{query}'\n")

    # Ask Neo4j for the 2 most similar tickets
    results = vector_store.similarity_search(query, k=2)

    for i, doc in enumerate(results):
        print(f"--- Result {i+1} ---")
        print(f"📄 Content: {doc.page_content}")
        print(f"📊 Metadata: {doc.metadata}")
        print("-" * 20)

if __name__ == "__main__":
    test_semantic_search()