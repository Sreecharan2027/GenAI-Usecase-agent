import streamlit as st
from duckduckgo_search import DDGS
import cohere
from dotenv import load_dotenv
import os
import faiss
import numpy as np
from fpdf import FPDF
from serpapi import GoogleSearch



load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

index = None
stored_chunks = []  
def duckduckgo_search(query):
    with DDGS() as ddgs:
        results = [r['body'] for r in ddgs.text(query, max_results=5)]
    return "\n\n".join(results)

def chunk_text(text, max_chunk_size=300):
    """Split text into smaller chunks for embedding"""
    sentences = text.split(". ")
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    chunks.append(current_chunk.strip())
    return chunks

def embed_and_store_chunks(chunks):
    global index, stored_chunks

    embeddings = co.embed(
        texts=chunks,
        model="embed-english-v3.0",
        input_type="search_document"
    ).embeddings

    embedding_dim = len(embeddings[0])  
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(np.array(embeddings).astype("float32"))

    stored_chunks = chunks  

def retrieve_relevant_context(query, top_k=5):
    global index, stored_chunks

    query_embed = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    ).embeddings

    D, I = index.search(np.array(query_embed).astype("float32"), top_k)
    return "\n".join([stored_chunks[i] for i in I[0]])

def cohere_rag_generate(query, context):
    """RAG-style generation with retrieved context"""
    prompt = f"""
You are an AI assistant. Use the context below to answer the user's request.
If the context is not sufficient, you may generalize based on your knowledge.

Context:
{context}

Question:
{query}

Answer in markdown format:
"""
    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=600,
        temperature=0.7,
        stop_sequences=["--END--"]
    )
    return response.generations[0].text.strip()

def serpapi_search_resources(query):
    try:
        if not SERPAPI_API_KEY:
            raise ValueError("SerpAPI key not found in .env file")

        search = GoogleSearch({
            "q": query,
            "api_key": SERPAPI_API_KEY
        })

        results = search.get_dict()
        if "organic_results" not in results or len(results["organic_results"]) == 0:
            raise ValueError("No resources found from SerpAPI")

        formatted_results = []
        for result in results["organic_results"][:5]:
            title = result.get("title", "No Title")
            link = result.get("link", "#")
            formatted_results.append(f"- [{title}]({link})")

        return "\n".join(formatted_results)

    except Exception as e:
        st.error(f"Error during resource search: {str(e)}")
        return "No resource links available. Please try again later."

def clean_text_for_pdf(text):
    return text.encode('latin1', 'ignore').decode('latin1')

def generate_pdf(industry_info, usecase_summary, resource_links, company_name):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, f"Final Proposal for {clean_text_for_pdf(company_name)}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, "Industry Overview", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, clean_text_for_pdf(industry_info))
    pdf.ln(10)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, "Top AI/ML/GenAI Use Cases", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, clean_text_for_pdf(usecase_summary))
    pdf.ln(10)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, "Resource Assets", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, clean_text_for_pdf(resource_links))


    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output


# Streamlit UI

st.set_page_config(page_title="GenAI Use Case Generator", layout="wide")
st.title("🧠 GenAI Use Case Generator (Cohere RAG)")
st.markdown("This tool uses Cohere RAG to research industries, generate use cases, and find datasets.")

company_name = st.text_input("Enter a Company or Industry Name:", "Toyota Motor Corporation")

if st.button("🔍 Run Use Case Generation"):
    with st.spinner("🔍 Researching industry/company..."):
        industry_info = duckduckgo_search(f"{company_name} industry segment and strategic focus areas")
        st.subheader("📊 Industry Info")
        st.write(industry_info)

    with st.spinner("🔗 Creating knowledge base..."):
        chunks = chunk_text(industry_info)
        embed_and_store_chunks(chunks)

    with st.spinner("⚙️ Generating AI/ML/GenAI Use Cases..."):
        context = retrieve_relevant_context("Generate top AI/ML/GenAI use cases")
        usecase_summary = cohere_rag_generate(
            "Generate top AI/ML/GenAI use cases that improve operations, automate workflows, and enhance customer experience. Include bonus use cases like RAG assistants or auto-reporting tools.",
            context
        )
        st.subheader("🧠 Suggested Use Cases")
        st.markdown(usecase_summary)

    with st.spinner("📚 Finding relevant datasets/resources..."):
        resource_links = serpapi_search_resources(f"{usecase_summary} dataset site:kaggle.com OR site:github.com")
        st.subheader("🔗 Datasets and Resource Links")
        st.markdown(resource_links)


    pdf_output = generate_pdf(industry_info, usecase_summary, resource_links, company_name)
    st.download_button(
        label="Download Proposal as PDF",
        data=pdf_output,
        file_name=f"final_proposal_{company_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

