from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

template = """
You are an ISO/IEC 27001:2022 implementation expert.
You will be given a template for a sample report in RTF. Use that report to create a similar report by summarizing the ISO assessment in HTML format.
These are the company names and contributers, Use these to replace the placeholders:
\"\"\"{companies}\"\"\"

Here is the report template:
\"\"\"{report}\"\"\"

And here is the ISO assessment:
\"\"\"{assessment}\"\"\"

Following is the date for today. Replace this date in placeholder:
\"\"\"{date}\"\"\"


You are to generate an HTML report using the following exact style and structure. Maintain all class names, spacing, colors, font usage, and component layout as shown below. Use this HTML template as a reference for any further content or sections.

--------------------------
HTML TEMPLATE STARTS HERE
--------------------------

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>[TITLE GOES HERE]</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    body {{
      font-family: 'Inter', sans-serif;
      background: #f9fafb;
      margin: 0;
      padding: 2rem;
      color: #1f2937;
    }}
    h1, h2, h3, h4 {{
      color: #111827;
      margin-bottom: 0.5rem;
    }}
    h1 {{
      font-size: 2.25rem;
      border-bottom: 3px solid #3b82f6;
      padding-bottom: 0.25rem;
      margin-bottom: 1.5rem;
    }}
    h2 {{
      font-size: 1.5rem;
      margin-top: 2rem;
      border-bottom: 2px solid #93c5fd;
      padding-bottom: 0.25rem;
    }}
    h3 {{
      font-size: 1.25rem;
      margin-top: 1.5rem;
      color: #2563eb;
    }}
    p {{
      line-height: 1.6;
      margin-top: 0.5rem;
      margin-bottom: 1rem;
    }}
    ul {{
      margin-top: 0.25rem;
      margin-bottom: 1rem;
      padding-left: 1.25rem;
    }}
    li {{
      margin-bottom: 0.4rem;
    }}
    .section {{
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgb(0 0 0 / 0.1);
      padding: 1.5rem 2rem;
      margin-bottom: 2rem;
    }}
    .highlight {{
      background-color: #dbeafe;
      border-left: 4px solid #3b82f6;
      padding: 0.75rem 1rem;
      margin: 1rem 0;
      border-radius: 4px;
      color: #1e40af;
    }}
    .status-ok {{
      color: #16a34a;
      font-weight: 600;
    }}
    .status-gap {{
      color: #dc2626;
      font-weight: 600;
    }}
    .note {{
      font-size: 0.9rem;
      color: #6b7280;
      font-style: italic;
      margin-top: -0.5rem;
      margin-bottom: 1rem;
    }}
    .participants-list {{
      list-style-type: disc;
      margin-left: 1.5rem;
    }}
    .table-container {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      margin-bottom: 1rem;
    }}
    th, td {{
      border: 1px solid #e5e7eb;
      padding: 0.75rem 1rem;
      text-align: left;
    }}
    th {{
      background-color: #e0e7ff;
      color: #3730a3;
    }}
    @media (max-width: 600px) {{
      body {{
        padding: 1rem;
      }}
      h1 {{
        font-size: 1.75rem;
      }}
      h2 {{
        font-size: 1.25rem;
      }}
    }}
  </style>
</head>
<body>

<main>
  <h1>[REPORT TITLE]</h1>

  <section class="section" id="section-id">
    <h2>[Section Heading]</h2>

    <h3>[Subheading]</h3>
    <p>[Paragraph of content]</p>

    <ul>
      <li>[Item 1]</li>
      <li>[Item 2]</li>
    </ul>

    <div class="highlight">
      [Highlighted callout text here]
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>[Column 1]</th>
            <th>[Column 2]</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>[Data 1]</td>
            <td>[Data 2]</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</main>

</body>
</html>
------------------------
HTML TEMPLATE ENDS HERE
------------------------

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
- Use the provided Company Names to fill the placeholders of the [company-name] and  [ - name-1 ..etc].
- Use the provided company name as the target comapany of audit and Vlectra as second company.
- Follow all class names and styling conventions exactly.
- Place new section content within `<section class="section">`.
- Use consistent typography hierarchy: `<h1>` for title, `<h2>` for main section, `<h3>` for sub-sections, etc.
- Use `.highlight` for improvement opportunities or callouts.
- Use `.status-gap` or `.status-ok` span or class for issue status tags.
- Wrap tabular data inside `.table-container` and use proper `<thead>/<tbody>` tags.
- Return the result as HTML. Do not include commentary or triple quotes.
"""

prompt = PromptTemplate(
    input_variables=["report", "assessment","companies","date"],
    template=template
)

def get_summary(llm):
    return LLMChain(llm=llm, prompt=prompt)
