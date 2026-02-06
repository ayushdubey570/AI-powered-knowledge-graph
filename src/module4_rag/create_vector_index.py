import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.graphs import Neo4jGraph

# --- CONFIGURATION ---
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Check credentials
if not NEO4J_URI or not NEO4J_PASSWORD:
    raise ValueError("❌ Error: Missing Neo4j credentials in .env file.")

def create_vector_index():
    print("⏳ Loading Embedding Model (this might take a minute)...")
    
    # 1. Initialize the Embedding Model (Free & Local)
    # This converts text into a list of 384 numbers
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("🔄 Connecting to Neo4j to build the Index...")

    # 2. Create the Vector Index on the 'Ticket' Node
    # We are indexing the 'description' property.
    # The index name will be "ticket_description_vector".
    try:
        vector_index = Neo4jVector.from_existing_graph(
            embedding=embeddings,
            url=NEO4J_URI,
            username=NEO4J_USER,
            password=NEO4J_PASSWORD,
            index_name="ticket_description_vector",  # The name of our new index
            node_label="Ticket",                     # The node we are indexing
            text_node_properties=["rag_content"],    # The text we want to search
            embedding_node_property="embedding",     # Where to save the vectors
        )
        print(f"✅ Success! Vector Index 'ticket_description_vector' created.")
        print("   The Graph is now ready for Semantic Search.")
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")

if __name__ == "__main__":
    create_vector_index()