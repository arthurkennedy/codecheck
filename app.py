import streamlit as st
import json
import os
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(page_title="CodeCheck AI", page_icon="🩺", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .result-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: white;
        border-left: 5px solid #007bff;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .issue-missing { border-left-color: #dc3545; }
    .issue-incorrect { border-left-color: #ffc107; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_guidelines():
    with open("data/coding_guidelines.json", "r") as f:
        return json.load(f)

# --- RAG UTILS ---
@st.cache_resource
def get_rag_engine():
    """Initialize and cache the RAG engine once per session."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return CodeCheckRAG(api_key)

class CodeCheckRAG:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.guidelines = load_guidelines()
        self.index = None
        self.texts = [f"{g['type']} {g['code']}: {g['description']}. Guideline: {g['guideline']}" for g in self.guidelines]
        self._prepare_index()

    def _prepare_index(self):
        response = self.client.embeddings.create(
            input=self.texts,
            model="text-embedding-3-small"
        )
        embeddings = np.array([data.embedding for data in response.data]).astype('float32')
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

    def search(self, query, k=2):
        response = self.client.embeddings.create(
            input=[query],
            model="text-embedding-3-small"
        )
        query_embedding = np.array([response.data[0].embedding]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        results = [self.texts[i] for i in indices[0]]
        return "\n\n".join(results)

# --- APP LOGIC ---
def validate_note(note_text, context):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are a professional medical coding auditor. Analyze the clinical note below using the provided coding guidelines.
    
    GUIDELINES:
    {context}
    
    CLINICAL NOTE:
    {note_text}
    
    TASK:
    Identify any coding issues (missing or incorrect codes). 
    Suggest the correct ICD-10 or CPT codes based on the guidelines.
    
    OUTPUT FORMAT:
    You MUST output ONLY valid JSON in this exact structure:
    {{
      "issues": [
        {{
          "type": "missing_code" | "incorrect_code",
          "description": "Short summary of the issue",
          "suggested_code": "The code string",
          "explanation": "Why this code is needed or why the original was wrong"
        }}
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a medical coding validation assistant."},
                      {"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# --- UI LAYOUT ---
def main():
    st.title("🩺 CodeCheck AI")
    st.markdown("### MVP: AI-Powered Clinical Coding Validation")

    api_key = os.getenv("OPENAI_API_KEY")

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        if api_key:
            st.success("✅ API key loaded from environment")
        else:
            st.error("❌ OPENAI_API_KEY not found in .env file")

        st.divider()
        st.markdown("### Sample Clinical Notes")
        samples = {
            "Select a sample...": "",
            "Sample 1: Routine HTN & Diabetes": "Patient presents for follow-up of hypertension and Type 2 diabetes. BP is 145/90. Patient continues Metformin. No complications noted today.",
            "Sample 2: Asthma Evaluation": "Patient reporting occasional wheezing and shortness of breath. History of asthma. No acute distress. 15-minute evaluation performed.",
            "Sample 3: Complex Follow-up": "Patient here for management of uncontrolled hypertension and new onset of wheezing. Spent 35 minutes discussing treatment plan and medication adjustments."
        }
        selected_sample = st.selectbox("Quick Load", list(samples.keys()))
        if selected_sample != "Select a sample...":
            st.session_state.note_input = samples[selected_sample]

    # Main Area
    note_text = st.text_area("Paste Clinical Note or Claim Text here:",
                             value=st.session_state.get('note_input', ''),
                             height=250,
                             placeholder="Patient presents with...")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        validate_btn = st.button("🚀 Validate Coding")

    if validate_btn:
        if not api_key:
            st.error("OPENAI_API_KEY is not set. Please add it to your .env file and restart the app.")
        elif not note_text.strip():
            st.warning("Please enter a clinical note to validate.")
        else:
            with st.spinner("Analyzing coding guidelines and clinical note..."):
                try:
                    rag = get_rag_engine()
                    if rag is None:
                        st.error("Failed to initialize RAG engine. Check your API key in .env.")
                    else:
                        context = rag.search(note_text)
                        results = validate_note(note_text, context)

                        if "error" in results:
                            st.error(f"Error: {results['error']}")
                        else:
                            st.subheader("Validation Results")
                            issues = results.get("issues", [])

                            if not issues:
                                st.success("No coding issues detected based on available guidelines.")
                            else:
                                for issue in issues:
                                    css_class = "issue-missing" if issue['type'] == "missing_code" else "issue-incorrect"
                                    type_label = "Missing Code" if issue['type'] == "missing_code" else "Incorrect Code"

                                    st.markdown(f"""
                                    <div class="result-card {css_class}">
                                        <h4 style="margin-top:0;">{type_label}: <span style="color:#007bff;">{issue['suggested_code']}</span></h4>
                                        <p><strong>Issue:</strong> {issue['description']}</p>
                                        <p><strong>Explanation:</strong> {issue['explanation']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)

                            with st.expander("View Raw JSON Output"):
                                st.json(results)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
