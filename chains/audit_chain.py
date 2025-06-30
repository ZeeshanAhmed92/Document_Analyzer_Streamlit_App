from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def analyze_module(llm):
    template = """
You are an ISO/IEC 27001:2022 Certified Lead Auditor.

Your task is to assess the provided document for compliance with the specified ISO/IEC 27001:2022 clauses and controls.

Use the following controls list for assessment:
{control_json}

---

Analyze the following document for the above controls:
\"\"\"{text}\"\"\"
---
Only output JSON in the following format (do not include any explanation):

[
  {{
    "Clause": "4.1",
    "Section": "4",
    "Control Id": "4.1",
    "Control Title": "Understanding the organization and its context",
    "Compliance": "✅",  // ✅ = Fully Compliant, 🟡 = Partially Compliant, ❌ = Not Compliant
    "Policy": "Summary of policies, procedures, or controls mentioned in the document relevant to this control",
    "Reference": "Quoted or paraphrased section(s) from the document used to assess compliance. Always mention file name.",
    "Evidence": "Describe any documented, physical, or digital evidence indicating implementation",
    "Gaps Identified": "Describe what is missing, unclear, or insufficient to meet the control. Leave blank if fully compliant.",
    "Recommended Action": "Action needed to address the gap or strengthen compliance"
  }}
]

Instructions:
* Check each control for explicit or implied coverage in the document.
* If a control is not addressed, mark it as "Compliance": "❌" and recommend what must be added.
* Use concise, clear language for all fields.
* Use the original control titles from the standard.
* Ensure the "Reference" contains relevant contextual support from the document.
* Make the "Recommended Action" field actionable and relevant to the gap.



"""

    prompt = PromptTemplate(
        input_variables=["text", "control_json"],
        template=template
    )

    return LLMChain(llm=llm, prompt=prompt)
