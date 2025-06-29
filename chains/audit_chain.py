from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def analyze_module(llm):
    template = """
You are a certified ISO/IEC 27001:2022 Lead Auditor.

You must analyze the provided document for compliance with the following controls:
{control_json}

---

Only output JSON in the following format (do not include any explanation):

[
  {{
    "Clause" : "4,5"
    "Section": "4",
    "Control Id": "4.1"
    "Control Title": "Title of the Control ID",
    "Compliance": "✅",  // or "🟡" or "❌"
    "Reference": "Reference to the context used to determine the gap."
    "Gaps Identified": "Describe gaps here or leave empty if none",
    "Recommended Action": "Specify actions to close the gap"
  }}
]

Instructions:
- For each clause/control, assess if it is addressed in the document.
- If a clause/control is not mentioned in the text, mark it ❌ and recommend what should be added.

Now analyze the following document:

\"\"\"{text}\"\"\"
"""

    prompt = PromptTemplate(
        input_variables=["text", "control_json"],
        template=template
    )

    return LLMChain(llm=llm, prompt=prompt)
