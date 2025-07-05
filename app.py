import os
import streamlit as st
import pandas as pd
import json
from langchain.callbacks import get_openai_callback
import nest_asyncio
import sys
from weasyprint import HTML
from bs4 import BeautifulSoup
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
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, streaming=False, api_key=OPENAI_API_KEY)

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

# Upload files
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(uploaded_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

# List current files in 'files' folder
existing_files = sorted([
    f for f in os.listdir(uploaded_folder)
    if f.lower().endswith((".pdf", ".docx"))
])

# Update session state for valid selections
st.session_state.policy_files = [
    f for f in st.session_state.policy_files if f in existing_files
]

# ─────────────── Uploaded Files with Delete Button (Table-Like) ───────────────
st.subheader("📋 Uploaded Files")

if existing_files:
    st.markdown("### File List")
    for file in existing_files:
        file_path = os.path.join(uploaded_folder, file)
        file_size = os.path.getsize(file_path) // 1024

        col1, col2, col3 = st.columns([5, 2, 1])
        col1.write(f"📄 **{file}**")
        col2.write(f"{file_size} KB")

        delete_key = f"delete_{file}"
        if col3.button("🗑️", key=delete_key):
            try:
                os.remove(file_path)
                st.success(f"Deleted: {file}")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting {file}: {e}")
else:
    st.info("No files uploaded yet.")

# ✅ Policy selector
st.sidebar.multiselect(
    "✅ Select policy documents:",
    options=existing_files,
    default=st.session_state.get("policy_files", []),
    key="policy_files"
)

# ─────────────── Run Analysis ───────────────
if st.button("🚀 Analyze", type="primary"):
    with st.spinner("📄 Extracting documents and analyzing..."):
        policy_text = read_folder_and_join_markdown(uploaded_folder, st.session_state.policy_files)
        evidence_text = read_folder_and_join_markdown_exclude(uploaded_folder, exclude_file_list=st.session_state.policy_files)

        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            final_results = asyncio.run(run_all_clauses(policy_text, llm, clauses))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            final_results = loop.run_until_complete(run_all_clauses(policy_text, llm, clauses))

        audit_df = pd.DataFrame(load_json_report(final_results))
        filtered_json = json.dumps(
            audit_df[["Control Id", "Clause", "Control Title", "Policy"]].to_dict(orient="records"), indent=2
        )

        evidence_result = evidence_chain.run(text=evidence_text, control_json=filtered_json)
        evidence_df = pd.DataFrame(load_json_report(evidence_result))

        merged_df = pd.merge(audit_df, evidence_df, on="Control Id", how="outer")
        merged_df['Evidence'] = merged_df['Evidence'].replace('', pd.NA).fillna('❌')

        merged_df.to_excel("./outputs/analysis.xlsx", index=False)

        doc = Document("./data/ISO 27001 - Valecta - Template - Report.docx")
        docx_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])

        summary_html = summary_chain.run(
            report=docx_text,
            assessment=merged_df.to_json(orient="records", indent=2)
        )

        soup = BeautifulSoup(summary_html, 'html.parser')
        abs_path = os.path.abspath("./data/Vlectra_logo.jpg")
        file_url = f"file://{abs_path}"
        img_tag = soup.new_tag("img", src=file_url, alt="Logo", style="width: 150px; height: auto;")
        soup.body.insert(0, img_tag)

        HTML(string=str(soup)).write_pdf("./outputs/Summary.pdf")

        with open("./outputs/summary.html", "w", encoding="utf-8") as f:
            f.write(summary_html)

        with open("./outputs/analysis.xlsx", "rb") as f:
            st.download_button("📥 Download Excel Report", f, file_name="audit_result.xlsx")

        with open("./outputs/summary.html", "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)

        st.success("✅ Analysis Complete!")

# ─────────────── Output File Downloads & Deletion ───────────────
st.sidebar.subheader("📁 Output Files")
output_folder = "./outputs"
os.makedirs(output_folder, exist_ok=True)

output_files = sorted(os.listdir(output_folder))
selected_output_files = st.sidebar.multiselect(
    "🗑️ Select output files to delete:",
    options=output_files,
    key="output_files_to_delete"
)

if st.sidebar.button("Delete Selected Output Files", type="secondary"):
    for file in selected_output_files:
        try:
            os.remove(os.path.join(output_folder, file))
            st.sidebar.success(f"Deleted: {file}")
        except Exception as e:
            st.sidebar.error(f"Error deleting {file}: {e}")
    st.rerun()

for file_name in output_files:
    file_path = os.path.join(output_folder, file_name)
    with open(file_path, "rb") as file:
        st.sidebar.download_button(
            label=f"📄 Download {file_name}",
            data=file,
            file_name=file_name,
            mime="application/octet-stream"
        )
