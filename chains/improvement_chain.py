from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

template = """
You are an ISO/IEC 27001:2022 implementation expert.

The following report outlines non-compliant or partially compliant areas from a compliance assessment.

Your job is to:
- Review the issues found.
- Suggest specific, actionable improvements for each area.
- Provide examples, templates, or documentation suggestions if needed.
- Clearly indicate which ISO 27001:2022 clause or control each suggestion relates to.

Here is the report:
\"\"\"{report}\"\"\"
"""

prompt = PromptTemplate(input_variables=["report"], template=template)

def get_improvement_chain(llm):
    return LLMChain(llm=llm, prompt=prompt)
