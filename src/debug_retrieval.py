import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def debug_search():
    print("🔎 Connecting to Vector Index...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Connect to the NEW index
    vector_store = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        index_name="ticket_description_vector",
        node_label="Ticket",
        text_node_properties=["rag_content"], # <--- WE MUST SEARCH THIS
        embedding_node_property="embedding",
    )

    query = "Dell XPS"
    print(f"\n❓ Querying for: '{query}'")
    
    # Get top 3 matches
    results = vector_store.similarity_search(query, k=3)

    print(f"\n📄 Found {len(results)} relevant tickets:\n")
    for i, doc in enumerate(results):
        print(f"--- MATCH #{i+1} ---")
        print(doc.page_content)
        print("--------------------")

if __name__ == "__main__":
    debug_search()