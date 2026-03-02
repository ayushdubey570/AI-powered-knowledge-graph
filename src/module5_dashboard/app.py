import streamlit as st
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv, find_dotenv
from streamlit_agraph import agraph, Node, Edge, Config

# LangChain & Neo4j Imports
from langchain_community.vectorstores import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from neo4j import GraphDatabase

# --- 1. PAGE CONFIGURATION & CSS ---
st.set_page_config(page_title="Enterprise Knowledge Graph", page_icon="🕸️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; font-family: 'Inter', sans-serif; }
    header {visibility: hidden;} footer {visibility: hidden;}
    .stat-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151; border-radius: 15px; padding: 20px; text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-5px); border-color: #6366f1; }
    .stat-value { font-size: 32px; font-weight: 700; color: #f3f4f6; }
    .stat-label { font-size: 14px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; }
    .user-msg {
        background-color: #2563eb; color: white; padding: 12px 18px; border-radius: 15px 15px 0 15px;
        margin: 10px 0; text-align: right; display: inline-block; max-width: 80%; float: right; clear: both;
    }
    .bot-msg {
        background-color: #374151; color: #e5e7eb; padding: 12px 18px; border-radius: 15px 15px 15px 0;
        margin: 10px 0; text-align: left; display: inline-block; max-width: 80%; float: left; clear: both;
    }
    .stTextInput input { border-radius: 20px; border: 1px solid #4b5563; background-color: #1f2937; color: white; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #374151; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOAD SECRETS (BULLETPROOF METHOD) ---
# find_dotenv() forces Python to search parent folders if app.py is buried in a subfolder
load_dotenv(find_dotenv())

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Failsafe: Stop the app immediately if the .env file isn't reading correctly
if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    st.error("🚨 CRITICAL ERROR: Could not read Neo4j credentials from .env file. Check your variable names and file path.")
    st.stop()

# --- 3. BACKEND LOGIC ---
@st.cache_resource
def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

driver = get_driver()

@st.cache_data(ttl=60)
def run_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters)
        return [record.data() for record in result]

@st.cache_resource
def get_graph_stats():
    try:
        t_count = run_query("MATCH (n:Ticket) RETURN count(n) as count")[0]["count"]
        c_count = run_query("MATCH (n:Customer) RETURN count(n) as count")[0]["count"]
        p_count = run_query("MATCH (n:Product) RETURN count(n) as count")[0]["count"]
        
        res_rate_data = run_query("""
            MATCH (t:Ticket) WITH toFloat(count(t)) AS total
            MATCH (t2:Ticket) WHERE toLower(t2.status) IN ['closed', 'resolved']
            WITH total, toFloat(count(t2)) AS closed_count
            RETURN CASE WHEN total = 0 THEN 0.0 ELSE (closed_count / total) * 100 END AS rate
        """)
        r_rate = f"{res_rate_data[0]['rate']:.1f}%" if res_rate_data else "N/A"
        return t_count, c_count, p_count, r_rate
    except Exception:
        return 0, 0, 0, "N/A"

@st.cache_resource
def load_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        index_name="ticket_description_vector",
        node_label="Ticket",
        text_node_properties=["rag_content"],
        embedding_node_property="embedding",
    )
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 100}),
        return_source_documents=False
    )
    return qa_chain

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://burstiq.com/wp-content/uploads/2023/09/Knowledge-Graph.png", use_container_width=True)    
    st.markdown("### AI Knowledge Graph\nEnterprise Intelligence System\n---")
    st.success("● Neo4j Database: Online")
    st.success("● Llama-3 Model: Ready")
    st.success("● Vector Index: Active")
    st.markdown("---")
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN HEADER & TABS ---
st.markdown("## 🕸️ AI Based Knowledge Graph Builder for Enterprise Intelligence")
st.markdown("Analyze support tickets, detect trends, and query customer data in real-time.")

tab1, tab2, tab3 = st.tabs(["📊 Executive Analytics", "💬 GraphRAG Copilot", "🕸️ Global Graph Explorer"])

# --- TAB 1: ANALYTICS ---
with tab1:
    st.write("")
    t_count, c_count, p_count, r_rate = get_graph_stats()
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="stat-card"><div class="stat-value">{t_count}</div><div class="stat-label">Total Tickets</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-card"><div class="stat-value">{c_count}</div><div class="stat-label">Unique Customers</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-card"><div class="stat-value">{p_count}</div><div class="stat-label">Products Tracked</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="stat-card"><div class="stat-value">{r_rate}</div><div class="stat-label">Resolution Rate</div></div>', unsafe_allow_html=True)
        
    st.divider()
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Tickets by Status")
        status_data = run_query("MATCH (t:Ticket) WHERE t.status IS NOT NULL RETURN t.status AS Status, count(t) AS Count")
        if status_data:
            fig1 = px.pie(pd.DataFrame(status_data), values='Count', names='Status', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No status property found on Ticket nodes.")
            
    with chart_col2:
        st.subheader("Top Products by Ticket Volume")
        # Updated to use the exact [:ABOUT] relationship we saw in your screenshot
        prod_data = run_query("""
            MATCH (t:Ticket)-[:ABOUT]->(p:Product)
            RETURN coalesce(p.name, p.id, "Unknown") AS Product, count(t) AS Volume
            ORDER BY Volume DESC LIMIT 5
        """)
        if prod_data:
            fig2 = px.bar(pd.DataFrame(prod_data), x='Product', y='Volume', color_discrete_sequence=['#6366f1'])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No relationships found connecting Tickets to Products.")

# --- TAB 2: CHAT ---
with tab2:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me about products, issues, or customer trends."}]

    for message in st.session_state.messages:
        role_class = "user-msg" if message["role"] == "user" else "bot-msg"
        st.markdown(f'<div style="overflow: hidden;"><div class="{role_class}">{message["content"]}</div></div>', unsafe_allow_html=True)

    st.write("") 
    if prompt := st.chat_input("Ex: 'Which product is failing the most?'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun() 

    # Handle response (after rerun)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner("🤖 Analyzing graph data points..."):
            try:
                qa_chain = load_rag_chain()
                
                # --- MEMORY EXTRACTION LOGIC ---
                # 1. Grab all past messages, skipping the first bot greeting and the newest user prompt
                past_messages = st.session_state.messages[1:-1]
                history_pairs = []
                temp_user_msg = None
                
                # 2. Loop through and group them into (User, AI) pairs
                for msg in past_messages:
                    if msg["role"] == "user":
                        temp_user_msg = msg["content"]
                    elif msg["role"] == "assistant" and temp_user_msg:
                        history_pairs.append((temp_user_msg, msg["content"]))
                        temp_user_msg = None
                
                # 3. Keep only the last 5 pairs (10 messages total) to prevent token overflow
                recent_history = history_pairs[-5:]
                # -------------------------------

                # Invoke the chain using "question" and our formatted "chat_history"
                response = qa_chain.invoke({
                    "question": st.session_state.messages[-1]["content"],
                    "chat_history": recent_history
                })
                
                # Note: ConversationalRetrievalChain returns the output under the key "answer", not "result"
                answer = response["answer"]
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as e:
                st.error(f"System Error: {e}")

# ==========================================
# TAB 3: GLOBAL GRAPH EXPLORER
# ==========================================
with tab3:
    st.header("Interactive Graph Network")
    st.caption("Live visualization of up to 50 active relationships in your database.")
    
    graph_data = run_query("""
        MATCH (n)-[r]->(m)
        RETURN elementId(n) as source_id, 
               labels(n)[0] as source_label, 
               coalesce(n.name, toString(n.id), toString(n.ticket_id), labels(n)[0]) as source_name,
               type(r) as rel_type,
               elementId(m) as target_id, 
               labels(m)[0] as target_label,
               coalesce(m.name, toString(m.id), toString(m.ticket_id), labels(m)[0]) as target_name
        LIMIT 50
    """)
    
    if graph_data:
        nodes, edges = [], []
        added_node_ids = set()
        
        # Upgraded color map to handle borders and backgrounds
        color_map = {
            "Customer": {"background": "#f59e0b", "border": "#d97706"}, 
            "Ticket": {"background": "#ef4444", "border": "#b91c1c"}, 
            "Product": {"background": "#3b82f6", "border": "#1d4ed8"}
        }
        
        for record in graph_data:
            s_id, s_lbl, s_name = record['source_id'], record['source_label'], record['source_name']
            t_id, t_lbl, t_name = record['target_id'], record['target_label'], record['target_name']
            
            if s_id not in added_node_ids:
                nodes.append(Node(
                    id=s_id, 
                    label=str(s_name), 
                    title=s_lbl, 
                    shape="ellipse", # <--- Forces text INSIDE the bubble
                    font={"color": "white", "size": 14, "face": "Inter"}, # <--- Crisp white text
                    color=color_map.get(s_lbl, {"background": "#9ca3af", "border": "#6b7280"})
                ))
                added_node_ids.add(s_id)
                
            if t_id not in added_node_ids:
                nodes.append(Node(
                    id=t_id, 
                    label=str(t_name), 
                    title=t_lbl, 
                    shape="ellipse", # <--- Forces text INSIDE the bubble
                    font={"color": "white", "size": 14, "face": "Inter"},
                    color=color_map.get(t_lbl, {"background": "#9ca3af", "border": "#6b7280"})
                ))
                added_node_ids.add(t_id)
                
            # Upgraded edges to look better in dark mode
            edges.append(Edge(
                source=s_id, 
                target=t_id, 
                label=record['rel_type'], 
                color="#9ca3af",
                font={"color": "#e5e7eb", "strokeWidth": 2, "strokeColor": "#0e1117"}
            ))
            
        config = Config(
            width="100%", 
            height=600, 
            directed=True, 
            physics=True, 
            hierarchical=False
        )
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.warning("No relationships found in the database.")