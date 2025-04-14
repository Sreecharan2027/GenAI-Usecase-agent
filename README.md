# 🧠 GenAI Use Case Generator (Cohere RAG)

This project is an AI-powered Streamlit app that helps generate tailored **AI/ML/GenAI use cases** for a given company or industry. It combines **Cohere's Retrieval-Augmented Generation (RAG)** with **DuckDuckGo Search**, **FAISS**, and **SerpAPI** to build contextual awareness and recommend relevant datasets or tools.

---

## 🚀 Features

- 🔍 Research industry/company insights using **DuckDuckGo**
- 🧠 Generate use cases with **Cohere's Command-R+**
- 🗃️ Retrieve relevant chunks using **FAISS vector search**
- 🔗 Discover datasets and assets via **SerpAPI**
- 📄 Download a full proposal as a **PDF report**
- 🎛️ Clean and intuitive **Streamlit UI**

---

## 📊 Architecture

```mermaid
flowchart TD
    A[User Inputs Company/Industry] --> B[DuckDuckGo Search]
    B --> C[Chunk & Embed with Cohere]
    C --> D[Store Chunks in FAISS Index]
    E[User Query: Use Case Generation] --> F[Query Embedding]
    F --> G[FAISS Search for Relevant Chunks]
    G --> H[Combine Query + Context for Prompt]
    H --> I[Cohere Command-R+ LLM Generation]
    I --> J[Generate Use Case Summary]
    J --> K[SerpAPI Google Search]
    K --> L[Retrieve Dataset/Resource Links]
    L --> M[FPDF Report Builder]
    M --> N[Download Final PDF Report]

````
## 💻 Tech Stack
 -   Frontend: Streamlit
 -  LLM & Embedding: Cohere
 -  Search: DuckDuckGo + SerpAPI (Google)
 -  Vector Store: FAISS
 -  PDF Generator: FPDF
 -  Language: Python

## 🧪 Example Use Case Output

**Company:** Toyota Motor Corporation

### ✅ Generated Use Cases:
- Predictive Maintenance using ML  
- GenAI Assistant for Customer Support  
- Automated Financial Reporting with RAG  
- Vehicle Image Captioning  
- Real-time Driver Alertness Detection  

### 🔗 Resource Links:
- [Kaggle datasets](https://www.kaggle.com/)
- [GitHub tools and repositories](https://github.com/)

