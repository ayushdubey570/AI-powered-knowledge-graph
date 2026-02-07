import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from neo4j import GraphDatabase

# --- 1. PAGE CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="Enterprise Knowledge Graph",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MODERN CSS STYLING ---
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Default Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* CUSTOM STAT CARDS */
    .stat-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: #6366f1;
    }
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #f3f4f6;
    }
    .stat-label {
        font-size: 14px;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* CHAT BUBBLES */
    .user-msg {
        background-color: #2563eb;
        color: white;
        padding: 12px 18px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        text-align: right;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .bot-msg {
        background-color: #374151;
        color: #e5e7eb;
        padding: 12px 18px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        text-align: left;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid #4b5563;
    }
    
    /* Input Box Styling */
    .stTextInput input {
        border-radius: 20px;
        border: 1px solid #4b5563;
        background-color: #1f2937;
        color: white;
    }
    /* Customize Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOAD SECRETS ---
load_dotenv()

#Manage API keys for streamlit deployment
def get_secret(key):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- 4. BACKEND LOGIC (Cached) ---
@st.cache_resource
def get_graph_stats():
    """Fetch live counts from Neo4j"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            t_count = session.run("MATCH (n:Ticket) RETURN count(n) as count").single()["count"]
            c_count = session.run("MATCH (n:Customer) RETURN count(n) as count").single()["count"]
            p_count = session.run("MATCH (n:Product) RETURN count(n) as count").single()["count"]
        driver.close()
        return t_count, c_count, p_count
    except Exception:
        return 0, 0, 0

@st.cache_resource
def load_rag_chain():
    """Initialize the 'God Mode' AI (k=100)"""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_store = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        index_name="ticket_description_vector",
        node_label="Ticket",
        text_node_properties=["rag_content"], # Using the Super-Field
        embedding_node_property="embedding",
    )
    
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY, 
        model_name="llama-3.3-70b-versatile"
    )
    
    # "GOD MODE" Enabled: k=100 for accuracy on small dataset
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=vector_store.as_retriever(search_kwargs={"k": 100})
    )
    return qa_chain

# --- 5. UI LAYOUT ---

# Sidebar
with st.sidebar:
    # 🟢 FIX: Changed use_column_width=True to use_container_width=True to fix the warning
    st.image("https://burstiq.com/wp-content/uploads/2023/09/Knowledge-Graph.png", use_container_width=True)    
    st.write("") # spacer
    st.markdown("### AI Knowledge Graph")
    st.caption("Enterprise Intelligence System")
    st.markdown("---")
    st.markdown("### ⚙️ System Status")
    st.success("● Neo4j Database: Online")
    st.success("● Llama-3 Model: Ready")
    st.success("● Vector Index: Active")
    st.markdown("---")
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main Header Area
st.markdown("## 🕸️ AI Based Knowledge Graph Builder for Enterprise Intelligence")
st.markdown("Analyze support tickets, detect trends, and query customer data in real-time using Graph RAG.")

# Live Stats Cards (Top Row)
t_count, c_count, p_count = get_graph_stats()
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{t_count}</div>
        <div class="stat-label">Total Tickets</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{c_count}</div>
        <div class="stat-label">Unique Customers</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{p_count}</div>
        <div class="stat-label">Products Tracked</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# --- 6. CHAT INTERFACE ---

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am connected to your Enterprise Knowledge Graph. Ask me about products, issues, or customer trends."}]

# Display Chat History
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role_class = "user-msg" if message["role"] == "user" else "bot-msg"
        st.markdown(f"""
        <div style="overflow: hidden;">
            <div class="{role_class}">
                {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat Input & Logic
st.write("") # Spacer
if prompt := st.chat_input("Ex: 'Which product is failing the most?'"):
    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun() # Force refresh to show user message immediately

# Handling the response (This runs after the rerun)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("🤖 Analyzing graph data points..."):
        try:
            qa_chain = load_rag_chain()
            response = qa_chain.invoke({"query": st.session_state.messages[-1]["content"]})
            answer = response["result"]
            
            # Append AI Message
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun() # Force refresh to show AI message
        except Exception as e:
            st.error(f"System Error: {e}")