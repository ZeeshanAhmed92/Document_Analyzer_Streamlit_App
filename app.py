from extractors.pdf_extractor import extract_text_from_pdf
from chains.audit_chain import get_audit_chain
from chains.improvement_chain import get_improvement_chain
from langchain_community.chat_models import ChatOpenAI
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()
print(os.getenv("OPENAI_API_KEY"))

file_path = "./files/Initial Implementation Plan - AI-Driven Document Compliance Analysis System (3).pdf"
controls = pd.read_json("ISO_27001_2022_Controls_List.json")


# text = extract_text_from_pdf(file_path)

# llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))

# audit_chain = get_audit_chain(llm)
# improvement_chain = get_improvement_chain(llm)

# print("🔍 Auditing...")
# audit_report = audit_chain.invoke({"document": text})
# print(audit_report)

# print("🔁 Suggesting Improvements...")
# fixes = improvement_chain.invoke({"report": audit_report})
# print(fixes)
