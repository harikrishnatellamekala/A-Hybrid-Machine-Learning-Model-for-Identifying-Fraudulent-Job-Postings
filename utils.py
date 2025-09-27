# utils.py
import pytesseract
from PIL import Image
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urlparse
import re

# Keep the exact same COLUMN_NAMES used for matching
COLUMN_NAMES = [
     "developer", "engineer", "manager", "executive", "analyst",
    "designer", "tester", "intern", "company", "salary",
    "location", "experience", "qualification", "skills", "responsibilities",
    "mca_registration","gstin","cin","iso_certification","pan_number",
    "tan_number","msme_registration","shop_license","import_export_code",
    "professional_tax","website_quality","domain_age","ssl_certificate",
    "linkedin_profile","glassdoor_reviews","employee_count","turnover",
    "contact_number","office_address","epf_registration"
]

def is_malicious_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return True
        if len(parsed.netloc) < 3:
            return True
        if parsed.scheme in ("javascript", "data"):
            return True
        return False
    except Exception:
        return True

def extract_text_from_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_link(link, timeout=8):
    if is_malicious_url(link):
        return f"__MALICIOUS_LINK__::{link}"
    try:
        response = requests.get(link, timeout=timeout, headers={"User-Agent":"Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script","style","noscript"]):
                script.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return text
        else:
            return ""
    except Exception as e:
        return f"Error extracting text from link: {str(e)}"

def write_to_csv(description, filename="uploaded_data.csv"):
    try:
        df_new = pd.DataFrame([[description]], columns=["description"])
        if os.path.exists(filename):
            df_old = pd.read_csv(filename)
            df_all = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_all = df_new
        df_all.to_csv(filename, index=False)
    except Exception as e:
        print(f"Error writing to CSV: {str(e)}")

def check_minimum_matches(description, threshold=3):
    """
    - If matches == 0 -> ❌ Not valid
    - If 1 <= matches <= 3 -> ❌ Not valid + count
    - If matches > 3 -> considered genuine (is_genuine True)
    """
    description_lower = description.lower()
    match_count = 0
    matched_cols = []
    for col in COLUMN_NAMES:
        if col.lower() in description_lower:
            match_count += 1
            matched_cols.append(col)

    if match_count == 0:
        msg = f"❌ Not a valid job profile! No matches found."
        return False, msg, match_count, matched_cols
    elif match_count <= 3:
        msg = f"❌ Not a valid job profile! Only {match_count} matches found."
        return False, msg, match_count, matched_cols
    else:
        msg = f"Matches found: {match_count}"
        return True, msg, match_count, matched_cols

def extract_job_details(description):
    details = {}

    title_match = re.search(r"(developer|engineer|manager|executive|analyst|designer|tester|intern)", description, re.I)
    if title_match:
        details["Job Title"] = title_match.group(0).title()

    company_match = re.search(r"(at\s+([A-Z][A-Za-z0-9& ]+))", description)
    if company_match:
        details["Company Name"] = company_match.group(2).strip()

    salary_match = re.search(r"(\d{4,6}\s?(?:INR|Rs|₹|USD|dollars)?)", description, re.I)
    if salary_match:
        details["Salary"] = salary_match.group(1)

    location_match = re.search(r"(Hyderabad|Bangalore|Chennai|Mumbai|Delhi|Remote|Onsite)", description, re.I)
    if location_match:
        details["Location"] = location_match.group(1)

    exp_match = re.search(r"(\d+\+?\s?years?)", description, re.I)
    if exp_match:
        details["Experience"] = exp_match.group(1)

    qual_match = re.search(r"(B\.Tech|MCA|MBA|CA|Degree|Diploma|Graduate)", description, re.I)
    if qual_match:
        details["Qualification"] = qual_match.group(1)

    if "responsibilit" in description.lower():
        details["Responsibilities"] = "Mentioned"

    if "skill" in description.lower():
        details["Skills"] = "Mentioned"

    if "about us" in description.lower() or "company" in description.lower():
        details["About Company"] = "Mentioned"

    if "remote" in description.lower():
        details["Job Mode"] = "Remote"
    elif "onsite" in description.lower():
        details["Job Mode"] = "Onsite"
    elif "part-time" in description.lower() or "part time" in description.lower():
        details["Job Mode"] = "Part-time"

    return details
