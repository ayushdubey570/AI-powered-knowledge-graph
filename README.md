# 🕸️ AI-Based Knowledge Graph Builder for Enterprise Intelligence

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Neo4j](https://img.shields.io/badge/Database-Neo4j%20Graph-green)
![Llama3](https://img.shields.io/badge/AI-Llama%203%20%2B%20LangChain-orange)

An end-to-end Enterprise Intelligence system that converts unstructured support ticket data into a structured Knowledge Graph. It utilizes **Graph RAG (Retrieval Augmented Generation)** to allow managers to "chat with their data," identifying trends, root causes, and product failures with high accuracy.

## 🚀 Project Architecture

The system is built in 5 modular stages:

1.  **Ingestion:** Normalizes raw CSV data (Support Tickets).
2.  **Extraction:** NLP pipeline to extract Entities (Customer, Product, Issue) and Relationships.
3.  **Graph Construction:** Builds a Neo4j Knowledge Graph with "Rich Context" nodes.
4.  **Vector Indexing:** Generates embeddings for Semantic Search using `sentence-transformers`.
5.  **Dashboard:** A Streamlit-based UI for real-time analytics and RAG-based chat.

## 📂 Project Structure

```bash
AI-POWERED-KNOWLEDGE-GRAPH/
├── data/                       # Data storage
│   ├── raw/                    # Original CSV files
│   └── processed/              # Cleaned CSVs and JSON triples
├── src/                        # Source code
│   ├── module1_ingestion/      # Data cleaning scripts
│   ├── module2_extraction/     # Entity extraction logic
│   ├── module3_graph_construction/ # Neo4j builder scripts
│   ├── module4_rag/            # Vector indexing and retrieval
│   └── module5_dashboard/      # Streamlit Web App
├── venv/                       # Virtual Environment
├── .env                        # API Keys (Neo4j, Groq)
├── requirements.txt            # Python dependencies
└── README.md                   # Main Project Documentation

```

---

## 🛠️ Setup & Installation

### 1. Prerequisites

* **Python 3.10** or higher
* **Neo4j AuraDB Account** (Free Tier is sufficient)
* **Groq API Key** (for accessing Llama 3)

### 2. Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd AI-POWERED-KNOWLEDGE-GRAPH

# Create Virtual Environment
python -m venv venv

# Activate Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

```

### 3. Configure Secrets

Create a `.env` file in the root directory and add your credentials:

```ini
NEO4J_URI=neo4j+s://<your-db-id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-db-password>
GROQ_API_KEY=<your-groq-api-key>

```

---

## ⚡ Quick Start (Run the Pipeline)

Follow these steps to build the system from scratch. Run all commands from the **root** directory.

### Step 1: Ingest & Clean Data

Loads raw tickets and normalizes text.

```bash
python -m src.module1_ingestion.normalize_tickets

```

### Step 2: Extract Entities

Extracts customers, products, and issues into structured JSON triples.

```bash
python -m src.module2_extraction.entity_extractor

```

### Step 3: Build Knowledge Graph

Pushes the structured data into Neo4j, creating nodes and relationships.

```bash
python -m src.module3_graph_construction.graph_builder

```

### Step 4: Create Vector Index (The Brain)

Generates embeddings for the graph to enable AI understanding.

```bash
python -m src.module4_rag.create_vector_index

```

### Step 5: Launch Dashboard 🚀

Starts the web application.

```bash
python -m streamlit run src/module5_dashboard/app.py

```

---

## 📚 Module Documentation

For detailed information on how each specific part works, please refer to the individual module documentation:

* **[Module 1: Ingestion & Normalization](src/module1_ingestion/README.md)**
* **[Module 2: Entity Extraction](src/module2_extraction/README.md)**
* **[Module 3: Graph Construction](src/module3_graph_construction/README.md)**
* **[Module 4: RAG & Vector Search](src/module4_rag/README.md)**
* **[Module 5: Intelligence Dashboard](src/module5_dashboard/README.md)**

---

## 🔮 Future Improvements

* Implement an **Agentic Router** to dynamically switch between Cypher queries (for counting) and Vector Search (for reasoning).
* Add support for **PDF/Email ingestion**.
* Expand the ontology to include "Departments" and "Agents".

---

**Author:** Ayush Kumar Dubey
**Project Type:** Enterprise AI / Knowledge Graph