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
    "Exact Evidence Extract": "Reference to evident of policy being implemented from Evidence Text. Donot refer to any material or text in or referred in Evidence Text",
    "Evidence Recommendation": "If applicable, include recommendation to improve evidence quality or implementation clarity. If none, return 'None'.",
    "Evidence": "✅" // Use ✅ only if evidence is present AND no recommendation is needed.
                  // Use 🟡 if evidence is present BUT improvement is recommended.
                  // Use ❌ if no evidence is found.
  }}
]

Instructions:
- Look for evidence only in "Evidence Text" and not the control_json. All file references should be from "Evidence Text".
- Match controls from `control_json` with relevant parts of the evidence text.
- "Policy Implementation Evidence": specify the file name or source where evidence is found.
- "Exact Evidence Extract": quote or paraphrase proof of implementation.
- "Evidence Recommendation": Provide a recommendation only if there is room for improvement. If fully compliant, write "None".
- "Evidence": Use:
  - ✅ if evidence is complete and needs no recommendation,
  - 🟡 if evidence is present but can be improved,
  - ❌ if no evidence is found.
-**Evidence can only be taken from Evidence Text. Do not refer to text in control_json***
- Just return the list of json no need for commentary, tags etc.
"""
    prompt = PromptTemplate(
        input_variables=["text", "control_json"],
        template=template
    )

    return LLMChain(llm=llm, prompt=prompt)
