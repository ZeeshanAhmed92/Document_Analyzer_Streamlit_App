from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def analyze_evidence(llm):
    template = """
You are an ISO/IEC 27001:2022 Lead Auditor.

Analyze the evidence document to verify whether the controls are implemented, and link this implementation to policy.

---

Controls to Check:
{control_json}

---

Evidence Text:
\"\"\"{text}\"\"\"

Respond only in the following JSON format:

[
  {{
    "Control Id": "4.1",
    "Policy Implementation Evidence": "evidence_context.pdf",
    "Exact Evidence Extract": "The organization conducted its 2023 context review...",
    "Evidence Recommendation": "Include documentation of stakeholder input in next review"
  }}
]

Instructions:
- Match controls from `control_json` with relevant parts of the evidence text.
- "Policy Implementation Evidence": specify the file name or source where evidence is found.
- "Exact Evidence Extract": quote or paraphrase proof of implementation.
- "Evidence Recommendation": mention how the evidence could be improved (e.g. more complete, clearer, updated).
"""
    prompt = PromptTemplate(
        input_variables=["text", "control_json"],
        template=template
    )

    return LLMChain(llm=llm, prompt=prompt)
