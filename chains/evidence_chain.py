from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def evidence_module(llm):
  template = """
You are an ISO/IEC 27001:2022 Certified Lead Auditor.

Your task is to update an existing ISO/IEC 27001:2022 compliance report by analysing the newly provided document for **evidence of control implementation**.

You will receive:
- `report_json`: A partially completed compliance report containing several ISO/IEC 27001:2022 controls.
- `text`: A newly provided document that may contain relevant evidence of implementation.

Your responsibilities:
- For **each control in `report_json`**, examine the `text` to locate **specific, verifiable evidence of implementation**, such as policies, procedures, reports, workflows, statements, or other documentation.
- **Do NOT reuse or rely on content already present in `report_json`.** Only extract new evidence from the current `text`.
- Update or add the following fields to each control based solely on what is found in `text`:
  - `"Implemented Evidence"`: Describe concrete evidence of implementation found in the document.
  - `"Evidence Reference"`: Provide the filename or section where the evidence was located. Always include the filename in parentheses.
  - `"Evidence Recommendation"`: Suggest additional documentation that would enhance the control’s evidential support, if current evidence is weak or missing.
---

Existing Compliance Report:
\"\"\"{report_json}\"\"\"

Document to Review:
\"\"\"{text}\"\"\"

---

**Output Format:**
Return a **valid JSON array**. Your output must follow the structure below:

[
  {{
    "Clause": "4.1",
    "Section": "4",
    "Control Id": "4.1",
    "Control Title": "Understanding the organization and its context",
    "Compliance": "✅",  // ✅ = Fully Compliant, 🟡 = Partially Compliant, ❌ = Not Compliant
    "Policy": "Summarize any documented policy, procedure, or implemented practice that relates to this control.",
    "Reference": "Quote or paraphrase the section(s) from the text that support your assessment. Always include the filename in parentheses, e.g., '(filename.pdf)'.",
    "Evidence Reference": "Filename or section where the evidence was found, e.g., '(filename.pdf)'.",
    "Implemented Evidence": "Describe specific evidence of implementation found in the text.",
    "Evidence Recommendation": "Recommend additional evidence or documentation, if applicable.",
    "Gaps Identified": "Identify what is missing or insufficient, if anything.",
    "Recommended Action": "Action required to close the gap or strengthen compliance."
  }}
]

---

**Important Rules:**
- "Update for all controls in `report_json` based on the new `text` such that all 93 controls are addressed."
- Only update fields based on what is found in the current `text`.
- If **no relevant evidence** is found in `text` for a control, set `"Compliance"` to ❌ and leave `"Implemented Evidence"` and `"Evidence Reference"` blank.
- **Always include the filename** in `"Evidence Reference"` and `"Reference"` when quoting or paraphrasing.
- **Do NOT include any output other than the JSON array.**
- Be clear, objective, and concise in all responses.
"""


  prompt = PromptTemplate(
      input_variables=["text", "report_json"],
      template=template
  )

  return LLMChain(llm=llm, prompt=prompt)
