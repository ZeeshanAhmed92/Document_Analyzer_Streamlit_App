import os
import streamlit as st
import pandas as pd
import json
from langchain.callbacks import get_openai_callback
import nest_asyncio
import sys
from utils.file_utils import read_folder_and_join_markdown, read_folder_and_join_markdown_exclude, get_controls
from utils.report_utils import load_json_report
from utils.llm_utils import run_all_clauses
from chains.audit_chain import analyze_module
from chains.evidence_chain import analyze_evidence
from chains.improvement_chain import get_improvement_chain
from chains.summary_report_chain import get_summary
from langchain.chat_models import ChatOpenAI
import asyncio
from docx import Document
from dotenv import load_dotenv
load_dotenv() 

nest_asyncio.apply()

# Streamlit page config
st.set_page_config(page_title="LLM Audit App", layout="wide")
st.title("📄 LLM Audit App")

# Set API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load controls and setup LLM
controls = pd.read_json("./data/ISO_27001_2022_Controls_List.json")
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, streaming=False, api_key=os.getenv("OPENAI_API_KEY"))

# Divide controls into 5 parts
clauses = get_controls(controls)

# Setup chains
audit_chain = analyze_module(llm)
evidence_chain = analyze_evidence(llm)
summary_chain = get_summary(llm)

# File handling
uploaded_folder = "files"
os.makedirs(uploaded_folder, exist_ok=True)

if "policy_files" not in st.session_state:
    st.session_state.policy_files = []

st.sidebar.header("📂 Upload Files")
uploaded_files = st.sidebar.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(uploaded_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    st.sidebar.success(f"Uploaded {len(uploaded_files)} files.")

    policy_selection = st.sidebar.multiselect(
        "✅ Select policy documents:", [file.name for file in uploaded_files],
        default=st.session_state.policy_files
    )
    st.session_state.policy_files = policy_selection


if st.button("🚀 Analyze", type="primary"):
    with st.spinner("📄 Extracting documents and analyzing..."):
        # Read policy and evidence documents
        policy_text = read_folder_and_join_markdown(uploaded_folder, st.session_state.policy_files)
        evidence_text = read_folder_and_join_markdown_exclude(uploaded_folder, exclude_file_list=st.session_state.policy_files)

        # Ensure compatibility on Windows
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run the async audit chain
        try:
            final_results = asyncio.run(run_all_clauses(policy_text,llm,clauses))
        except RuntimeError:
            # Handle "event loop already running" (e.g. in Jupyter/Colab)
            loop = asyncio.get_event_loop()
            final_results = loop.run_until_complete(run_all_clauses(policy_text,llm,clauses))

        # Load and process audit result
        audit_df = pd.DataFrame(load_json_report(final_results))
        filtered_json = json.dumps(
            audit_df[["Control Id", "Clause", "Control Title", "Policy"]].to_dict(orient="records"), indent=2
        )

        # Run evidence chain
        evidence_result = evidence_chain.run(text=evidence_text, control_json=filtered_json)
        evidence_df = pd.DataFrame(load_json_report(evidence_result))

        # Merge results
        merged_df = pd.merge(audit_df, evidence_df, on="Control Id", how="outer")
        merged_df['Evidence'] = merged_df['Evidence'].replace('', pd.NA).fillna('❌')

        
        # Save results
        merged_df.to_excel("./data/analysis.xlsx", index=False)

        doc = Document("./data/ISO 27001 - Valecta - Template - Report.docx")
        docx_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])


        # Run summary chain
        summary_html = summary_chain.run(report=docx_text, assessment=merged_df.to_json(orient="records", indent=2))

        with open("./data/summary.html", "w", encoding="utf-8") as f:
            f.write(summary_html)

        # Display download and summary
        with open("./data/analysis.xlsx", "rb") as f:
            st.download_button("📥 Download Excel Report", f, file_name="audit_result.xlsx")

        with open("./data/summary.html", "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)

        st.success("✅ Analysis Complete!")