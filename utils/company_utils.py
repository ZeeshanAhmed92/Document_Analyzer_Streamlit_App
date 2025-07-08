import json
import os

COMPANY_FILE = "./data/companies.json"

def load_companies():
    if os.path.exists(COMPANY_FILE):
        with open(COMPANY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_companies(companies):
    with open(COMPANY_FILE, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2)

def delete_company(companies, company_name):
    if company_name in companies:
        del companies[company_name]
        save_companies(companies)

def delete_contributor(companies, company_name, contributor_name):
    if company_name in companies and contributor_name in companies[company_name]:
        companies[company_name].remove(contributor_name)
        save_companies(companies)
