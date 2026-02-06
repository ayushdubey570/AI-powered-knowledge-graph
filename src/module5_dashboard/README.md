# 🖥️ Module 5: Enterprise Intelligence Dashboard

**Status:** ✅ Active | **Tech:** Streamlit, LangChain, Groq, CSS

This module is the **User Interface (UI)** of the project. It is a modern, full-stack web application that allows non-technical users (managers, executives) to interact with the underlying Knowledge Graph and Vector Database. It features a "God Mode" chat interface for high-accuracy analytics and real-time database statistics.

---

## 🎯 Purpose & Goals

1.  **Visualize:** Display real-time statistics from the Neo4j Graph (Total Tickets, Customers, Products).
2.  **Interact:** Provide a chat interface where users can ask questions in plain English (e.g., "Which product is failing?").
3.  **Retrieve:** Use **RAG (Retrieval Augmented Generation)** to fetch relevant tickets from the vector index and generate accurate answers using **Llama 3**.
4.  **UX Design:** Deliver a professional "Dark Mode" experience with glassmorphism effects and custom CSS.

---

## ⚙️ Workflow

```mermaid
graph TD
    A[User Query] -->|Input| B(Streamlit App)
    B -->|Check Cache| C{Model Loaded?}
    C -- No --> D[Load Llama 3 & Vector Store]
    C -- Yes --> E[Run Retrieval Chain]
    E -->|Retrieve k=100 Docs| F[(Neo4j Vector Index)]
    F -->|Return Context| G[LLM (Llama 3)]
    G -->|Generate Answer| H[Chat UI]

```

---

## 📂 File Structure

```bash
src/module5_dashboard/
├── __init__.py           # Package marker
├── app.py                # Main Streamlit Application
├── debug_retrieval.py    # Script to inspect raw search results
└── README.md             # This documentation

```

---

## 🚀 How to Run

Execute this command from the **root directory**:

```bash
python -m streamlit run src/module5_dashboard/app.py

```

**Access the App:**

* **Local URL:** `http://localhost:8501`
* **Network URL:** (Displayed in terminal for local network access)

---

## 🧠 Logic: "God Mode" Retrieval

A key feature of this dashboard is the **high-recall retrieval strategy** to ensure accurate counting and summarization on smaller datasets.

In `app.py`:

```python
# "GOD MODE" Enabled: k=100
qa_chain = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=vector_store.as_retriever(search_kwargs={"k": 100})
)

```

* **Standard RAG:** Usually retrieves `k=3` or `k=5` documents.
* **Our Project:** Retrieves `k=100`.
* **Why?** Since our dataset is small (~100 tickets), scanning the *entire* database ensures the AI never misses a trend or gives a "hallucinated" count. It effectively turns the RAG system into an analytical engine.

---

## 🎨 UI & Styling

The application uses custom HTML/CSS injection to override the default Streamlit look:

* **Theme:** Dark Mode (`#0e1117` background).
* **Stat Cards:** Custom HTML `<div>` elements with gradient backgrounds and hover effects.
* **Chat Bubbles:** Styled to mimic modern messaging apps (Blue for User, Grey for AI).
* **Sidebar:** Includes a dynamic status monitor and a professional abstract network image.

---

## 🛠️ Configuration

* **Change LLM:** To use a different model (e.g., `mixtral-8x7b`), update the `model_name` parameter in the `ChatGroq` initialization inside `app.py`.
* **Adjust "God Mode":** If the dataset grows to 10,000+ rows, **reduce `k` to 10 or 20** to prevent crashing the LLM context window.
* **Update Secrets:** Ensure `GROQ_API_KEY` is set in your `.env` file for the chat to function.

---

## 🔗 Project Completion

Congratulations! This is the final module.

* **Back to Root:** [Project Home](../../README.md)
