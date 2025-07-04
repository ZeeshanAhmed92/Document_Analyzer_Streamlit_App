from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

template = """
You are an ISO/IEC 27001:2022 implementation expert.
You will be given a template for a sample report. Use that report to make a similar report after summrizing the ISO assesment.
Comapny name is :
["Vlectra"]

Here is the report template:
\"\"\"{report}\"\"\"
And here is the Iso assesment.
\"\"\"{assesment}\"\"\"

*Make sure all of the following points are addressed*
1. Scope of the GAP
1.1 Applicability
1.2 Participants in the Audit
1.3 Audit Criteria
1.4 Audit Objectives
1.5 Scope of Entities Included in the Internal Audit
2. Executive Summary
2.1 Sampling Methodology
2.2 General Impressions of the Management System
2.2.1 Highlights
2.2.2 Findings
2.2.3 Non-conformities identified
2.2.4 Opportunities for improvement


**Instructions**
Use the provided Company names to fill the place holders in the template. 
Also add proper rtf headings and keep all heading blue and Everything else black. Format the structure and file properly.
Reutrn the result as rtf format. So that it is docx friendly. Color and format accordingly. Just return plain rtf text.
"""

prompt = PromptTemplate(input_variables=["report","assesment"], template=template)

def get_summary(llm):
    return LLMChain(llm=llm, prompt=prompt)
