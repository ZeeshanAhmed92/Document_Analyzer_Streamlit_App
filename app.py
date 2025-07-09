import os
import streamlit as st
import pandas as pd
import json
from langchain.callbacks import get_openai_callback
import nest_asyncio
import sys
from utils.company_utils import load_companies, save_companies, delete_company, delete_contributor
from utils.file_utils import read_folder_and_join_markdown, read_folder_and_join_markdown_exclude, get_controls
from utils.report_utils import load_json_report
from utils.llm_utils import run_all_clauses
from chains.audit_chain import analyze_module
from chains.evidence_chain import analyze_evidence
from chains.improvement_chain import get_improvement_chain
from chains.summary_report_chain import get_summary
from langchain.chat_models import ChatOpenAI
import asyncio
from weasyprint import HTML
from bs4 import BeautifulSoup
import os
from docx import Document
from dotenv import load_dotenv
from datetime import datetime
import base64

load_dotenv()
nest_asyncio.apply()

st.set_page_config(page_title="Valecta AI Auditor", layout="wide")

# Function to encode image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

# Encode your local background image
img_path = "./data/valecta.jpg"  # Replace with your local image path
img_base64 = get_base64_image(img_path)

# Inject custom CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        z-index: -1;
    }}

    h1 {{
        text-align: center;
        color: white;
        font-size: 2.5em;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Center-aligned custom title using HTML
st.markdown(
    """
    <h1 style='text-align: center; font-size: 2.5em; color: #42eff5'>📄 Valecta AI - The Auditor</h1>
    """,
    unsafe_allow_html=True
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load controls and setup LLM
controls = pd.read_json("./data/ISO_27001_2022_Controls_List.json")
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0, streaming=False, api_key=OPENAI_API_KEY)
clauses = get_controls(controls)



if "companies" not in st.session_state:
    st.session_state.companies = load_companies()




# Setup chains
audit_chain = analyze_module(llm)
evidence_chain = analyze_evidence(llm)
summary_chain = get_summary(llm)

# Directories
uploaded_folder = "files"
output_folder = "./outputs"
os.makedirs(uploaded_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Initialize session state
if "policy_files" not in st.session_state:
    st.session_state.policy_files = []

if "companies" not in st.session_state:
    st.session_state.companies = {}

# --- Sidebar Upload + File Management ---
st.markdown(
    """
    <style>
    /* Fully transparent sidebar background */
    section[data-testid="stSidebar"] {
        background-color: transparent !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
    }

    /* Set sidebar text color to #42eff5 */
    section[data-testid="stSidebar"] * {
        color: #42eff5 !important;
    }

    /* Optional: Customize checkbox and radio colors */
    input[type="checkbox"], input[type="radio"] {
        accent-color: #42eff5 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.header("📂 Upload Files")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(uploaded_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Uploaded {len(uploaded_files)} files.")

existing_files = sorted([
    f for f in os.listdir(uploaded_folder)
    if f.lower().endswith((".pdf", ".docx"))
])

# File selection + delete
st.sidebar.subheader("📑 Uploaded Files (Select Policy Files)")
for file in existing_files:
    col1, col2 = st.sidebar.columns([4, 1])
    with col1:
        checked = file in st.session_state.policy_files
        st.session_state[f"chk_{file}"] = st.checkbox(file, value=checked, key=f"chkbox_{file}")
    with col2:
        if st.button("❌", key=f"del_{file}"):
            os.remove(os.path.join(uploaded_folder, file))
            st.session_state.policy_files = [
                f for f in st.session_state.policy_files if f != file
            ]
            st.rerun()

# Update selected policy files
st.session_state.policy_files = [
    f for f in existing_files if st.session_state.get(f"chk_{f}", False)
]

# --- Company Info ---
st.markdown(
    "<h3 style='color: #42eff5;'>🏢 Company Information</h3>",
    unsafe_allow_html=True
)

st.markdown("""
<style>
/* Corrected selector for the main radio group label (e.g., 'Company Mode') */
div[data-testid="stRadio"] > div:first-child {
    color: #42eff5 !important;
    font-weight: 700 !important;
    font-size: 1.2rem !important;
}

/* Radio option labels */
div[data-testid="stRadio"] label {
    color: #42eff5 !important;
    font-weight: 500 !important;
    font-size: 1.05rem !important;
}

/* Radio button accent color */
div[data-testid="stRadio"] input[type="radio"] {
    accent-color: #42eff5 !important;
}
</style>
""", unsafe_allow_html=True)



company_names = list(st.session_state.companies.keys())
company_mode = st.radio("Company Mode", ["Select Existing", "Create New"], horizontal=True)

selected_companies = []

if company_mode == "Create New":
    new_company_name = st.text_input("Enter new company name:")
    # When creating a new company
    if new_company_name:
        if new_company_name not in st.session_state.companies:
            st.session_state.companies[new_company_name] = []
            save_companies(st.session_state.companies)
            st.rerun() 
        selected_companies = [new_company_name]
else:
    selected_companies = st.multiselect("Select one or more companies", company_names)

if selected_companies:
    st.markdown(f"**Selected Companies:** {', '.join(selected_companies)}")

    # Merge all contributors from selected companies
    all_contributors = set()
    for company in selected_companies:
        all_contributors.update(st.session_state.companies.get(company, []))
    all_contributors = list(all_contributors)

    selected_contributors = st.multiselect(
        "Contributors from all selected companies:",
        options=all_contributors,
        default=all_contributors,
        key="contributors_global"
    )

    new_contributor = st.text_input("Add a new contributor:")
    if st.button("➕ Add Contributor"):
        if new_contributor:
            for company in selected_companies:
                if new_contributor not in st.session_state.companies[company]:
                    st.session_state.companies[company].append(new_contributor)
            save_companies(st.session_state.companies)
            st.rerun() 
            st.success(f"Added contributor '{new_contributor}' to selected companies.")
            selected_contributors.append(new_contributor)


st.markdown(
    "<h3 style='color: #42eff5;'>Manage Companies & Contributors</h3>",
    unsafe_allow_html=True
)

# Delete companies
company_to_delete = st.selectbox("Delete a company:", company_names, key="delete_company")
if st.button("❌ Delete Company"):
    delete_company(st.session_state.companies, company_to_delete)
    st.success(f"Deleted company: {company_to_delete}")
    st.rerun()

# Delete contributor
if selected_companies:
    company_for_contrib = st.selectbox("Select company to delete contributor from:", selected_companies)
    contributors = st.session_state.companies.get(company_for_contrib, [])
    if contributors:
        contributor_to_delete = st.selectbox("Delete a contributor:", contributors, key="delete_contrib")
        if st.button("🗑️ Delete Contributor"):
            delete_contributor(st.session_state.companies, company_for_contrib, contributor_to_delete)
            st.success(f"Deleted contributor: {contributor_to_delete}")
            st.rerun()
    else:
        st.info("No contributors to delete.")



# --- Check Validity Before Analysis ---
can_analyze = (
    len(st.session_state.policy_files) > 0 and
    len(selected_companies) > 0 and
    len(selected_contributors) > 0
)

if not can_analyze:
    st.warning("Please ensure you have selected at least one policy document, one or more companies, and at least one contributor.")

# --- Analysis Button ---
if st.button("🚀 Analyze", type="primary", disabled=not can_analyze):
    with st.spinner("📄 Extracting documents and analyzing..."):
        status_box = st.empty() 
        # Extract policy/evidence text
        status_box.markdown("📄 Extracting Files, Step 1/4...")
        policy_text = read_folder_and_join_markdown(uploaded_folder, st.session_state.policy_files)
        evidence_text = read_folder_and_join_markdown_exclude(uploaded_folder, exclude_file_list=st.session_state.policy_files)

        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            status_box.markdown("📄 Extracting Policies, Step 2/4...")
            final_results = asyncio.run(run_all_clauses(policy_text, llm, clauses))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            final_results = loop.run_until_complete(run_all_clauses(policy_text, llm, clauses))

        audit_df = pd.DataFrame(load_json_report(final_results))
        filtered_json = json.dumps(
            audit_df[["Control Id", "Clause", "Control Title", "Policy"]].to_dict(orient="records"), indent=2
        )
        status_box.markdown("📄 Extracting Evidence, Step 3/4...")
        evidence_result = evidence_chain.run(text=evidence_text, control_json=filtered_json)
        evidence_df = pd.DataFrame(load_json_report(evidence_result))
        print(evidence_df)
        merged_df = pd.merge(audit_df, evidence_df, on="Control Id", how="outer")
        merged_df['Evidence'] = merged_df['Evidence'].replace('', pd.NA).fillna('❌')

        merged_df.to_excel(os.path.join(output_folder, "analysis.xlsx"), index=False)

        doc = Document("./data/ISO 27001 - Valecta - Template - Report.docx")
        docx_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""])
        metadata = f"Companies: {', '.join(selected_companies)}Contributors:</b> {', '.join(selected_contributors)}"

        metadata_json = [
            {
                "company": company,
                "contributors": st.session_state.companies[company]
            }
            for company in selected_companies
        ]
        print(metadata)
        from datetime import datetime
        status_box.markdown("📄 Generating Report, Step 4/4...")
        summary_html = summary_chain.run(
            report=docx_text,
            assessment=merged_df.to_json(orient="records", indent=2),
            companies=metadata_json,
            date=datetime.today().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
        )

        # Assuming `result` contains your HTML string
        soup = BeautifulSoup(summary_html, 'html.parser')
        # Get absolute file path and convert to file URL
        abs_path = os.path.abspath("./data/Vlectra_logo.jpg")
        file_url = f"file://{abs_path}"

        # Insert image with absolute file path
        img_tag = soup.new_tag(
            "img",
            src=file_url,  # or base64 version
            alt="Logo",
            style="width: 150px; height: auto;"  # Adjust as needed
        )
        soup.body.insert(0, img_tag)
        # Generate PDF
        HTML(string=str(soup)).write_pdf("./outputs/summary.pdf")




        with open(os.path.join(output_folder, "summary.html"), "w", encoding="utf-8") as f:
            f.write(metadata + summary_html)
            
        st.success("✅ Analysis Complete!")


st.markdown(
    "<h3 style='color: #42eff5;'>📁 Download Output Files</h3>",
    unsafe_allow_html=True
)

output_folder = "./outputs"  # replace with your actual path
output_files = os.listdir(output_folder)

if output_files:
    for file_name in output_files:
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, "rb") as file:
            st.download_button(
                label=f"📄 Download {file_name}",
                data=file,
                file_name=file_name,
                mime="application/octet-stream"
            )
else:
    st.info("No output files found yet.")