from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def analyze_module_1(text):
    prompt = f"""
You are a certified ISO/IEC 27001:2022 Lead Auditor.

You must analyze the provided document for compliance with the following:

---

### 📘 Core Clauses:

- Clause 4: Context of the organization  
- Clause 5: Leadership  
- Clause 6: Planning  

---

### 📘 Annex A.5 – Organizational Controls (A.5.1 to A.5.37):

You are required to evaluate **all** of these controls one by one, even if the document does not mention them explicitly.

---

### 🔍 Your Output Must Include:

#### 📄 Table 1 – Clauses

| Clause | Title | Compliance (✅ / 🟡 / ❌) | Gaps Identified | Recommended Action |
|--------|-----------------------------|------------------|------------------|---------------------|
| 4      | Context of the organization | ...              | ...              | ...                 |
| 5      | Leadership                  | ...              | ...              | ...                 |
| 6      | Planning                    | ...              | ...              | ...                 |

#### 📄 Table 2 – Annex A.5 Controls

| Control ID | Control Title | Compliance (✅ / 🟡 / ❌) | Notes / Gaps | Suggested Implementation |
|------------|----------------|--------------------------|------------------|----------------------------|
| A.5.1      | Policies for information security | ... | ... | ... |
| A.5.2      | Information security roles and responsibilities | ... | ... | ... |
| A.5.3      | Segregation of duties | ... | ... | ... |
...
| A.5.37     | Information security continuity | ... | ... | ... |

---

If a clause/control is not mentioned in the text, mark it ❌ and suggest what needs to be added or changed.

Now analyze the following document:

\"\"\"{text}\"\"\"
"""
    return prompt

def analyze_module_2(text):
    prompt = f"""
You are a certified ISO/IEC 27001:2022 Lead Auditor.

Analyze the document for compliance with:

---

### 📘 Core Clauses:

- Clause 7: Support  
- Clause 8: Operation  

---

### 📘 Annex A.6 – People Controls

- A.6.1 to A.6.8  

### 📘 Annex A.7 – Physical Controls

- A.7.1 to A.7.6  

---

### 🔍 Output Tables Required:

#### 📄 Table 1 – Clauses

| Clause | Title | Compliance (✅ / 🟡 / ❌) | Gaps Identified | Recommended Action |
|--------|-----------------------------|------------------|------------------|---------------------|
| 7      | Support                     | ...              | ...              | ...                 |
| 8      | Operation                   | ...              | ...              | ...                 |

#### 📄 Table 2 – A.6–A.7 Controls

| Control ID | Control Title | Compliance (✅ / 🟡 / ❌) | Notes / Gaps | Suggested Implementation |
|------------|----------------|--------------------------|------------------|----------------------------|
| A.6.1      | Screening | ... | ... | ... |
| A.6.2      | Terms and conditions of employment | ... | ... | ... |
...
| A.7.6      | Clear desk policy | ... | ... | ... |

---

⚠️ If a control or clause is missing in the document, clearly mark it ❌ and recommend what should be implemented.

Now analyze this content:

\"\"\"{text}\"\"\"
"""
    return prompt

def analyze_module_3(text):
    prompt = f"""
You are a certified ISO/IEC 27001:2022 Lead Auditor.

Analyze the following document for compliance with:

---

### 📘 Core Clauses:

- Clause 9: Performance Evaluation  
- Clause 10: Improvement  

---

### 📘 Annex A.8 – Technological Controls (A.8.1 to A.8.35)

---

### 🔍 Output Tables Required:

#### 📄 Table 1 – Clauses

| Clause | Title | Compliance (✅ / 🟡 / ❌) | Gaps Identified | Recommended Action |
|--------|-----------------------------|------------------|------------------|---------------------|
| 9      | Performance evaluation      | ...              | ...              | ...                 |
| 10     | Improvement                 | ...              | ...              | ...                 |

#### 📄 Table 2 – Annex A.8 Controls

| Control ID | Control Title | Compliance (✅ / 🟡 / ❌) | Notes / Gaps | Suggested Implementation |
|------------|----------------|--------------------------|------------------|----------------------------|
| A.8.1      | User end-point devices | ... | ... | ... |
| A.8.2      | Privileged access rights | ... | ... | ... |
...
| A.8.35     | Web filtering | ... | ... | ... |

---

If the document does not address a control, mark it ❌ and give actionable suggestions.

Now analyze the following text:

\"\"\"{text}\"\"\"
"""
    return prompt
