import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

# --- CONFIGURATION ---
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def run_chat_agent():
    print("⏳ Loading AI Models...")
    
    # 1. The Embedding Model (To understand your question)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 2. The Connect to Graph (To find the facts)
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

    # 3. The LLM (To write the answer)
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY, 
        model_name="llama-3.3-70b-versatile"
    )

    # 4. The Chain (Glues them together)
    # "stuff" means: Stuff the found documents into the prompt and ask LLM to summarize.
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=vector_store.as_retriever(search_kwargs={"k": 2})
    )

    # --- INTERACTIVE LOOP ---
    print("\n🤖 Graph RAG Agent is Online! (Type 'exit' to stop)")
    print("--------------------------------------------------")
    
    while True:
        query = input("\n❓ Ask a question about your tickets: ")
        if query.lower() in ["exit", "quit"]:
            break
        
        try:
            print("Thinking...")
            response = qa_chain.invoke({"query": query})
            print(f"\n💡 Answer: {response['result']}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_chat_agent()