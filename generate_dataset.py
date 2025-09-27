# generate_dataset.py
import pandas as pd
import random
import csv

# We'll create 1000 rows combining boolean-like columns and a short description
N = 1000
rows = []
for i in range(N):
    # randomly pick real or fake
    fraudulent = random.choices([0,1], weights=[0.6,0.4])[0]  # 60% genuine, 40% fake-ish
    website_quality = random.choice(["Excellent","Good","Average","Poor"])
    email_domain = random.choice(["Company Domain","Gmail","Outlook","Yahoo"])
    linkedin_activity = random.choice(["Active","Inactive"])
    scam_reports = random.choice(["None","Few","Many"])
    job_platform = random.choice(["LinkedIn","Indeed","Naukri","WhatsApp","Telegram"])
    salary_realism = random.choice(["Realistic","High","Low"])
    upfront_payment = random.choice(["Yes","No"])
    description_quality = random.choice(["Good","Average","Poor"])
    interview_process = random.choice(["In-Person","Video","Phone","None"])
    comm_channels = random.choice(["Email","WhatsApp","Telegram","Call"])
    has_company_logo = random.choice(["Yes","No"])
    social_media = random.choice(["Active","Inactive"])
    employee_reviews = random.choice(["Positive","Negative","None"])
    physical_address = random.choice(["Present","None"])
    epf_registration = random.choice(["Yes","No"])
    fssai_license = random.choice(["Yes","No","None"])
    sebi_approval = random.choice(["Yes","No","None"])
    description = random.choice([
        "Looking for software engineer with 2+ years experience in python and django",
        "Urgent requirement for developer. Apply now with resume",
        "Hiring marketing executive with good comm skills and sales experience",
        "Job opening in finance. CA preferred. Salary competitive",
        "Frontend developer required - html css js"
    ])
    # mca/gstin/cin fields as simple Yes/No/None
    mca_registration = random.choice(["Yes","No","None"])
    gstin = random.choice(["Yes","No","None"])
    cin = random.choice(["Yes","No","None"])
    iso_certification = random.choice(["Yes","No","None"])
    pan_number = random.choice(["Yes","No","None"])
    tan_number = random.choice(["Yes","No","None"])
    msme_registration = random.choice(["Yes","No","None"])
    shop_license = random.choice(["Yes","No","None"])
    import_export_code = random.choice(["Yes","No","None"])
    professional_tax = random.choice(["Yes","No","None"])

    row = [
        mca_registration,gstin,cin,iso_certification,pan_number,tan_number,msme_registration,
        shop_license,import_export_code,professional_tax,website_quality,"1 year", "Valid SSL",
        "https://linkedin.example","Good", "50", "10L", "1234567890", "Some Address", epf_registration,
        website_quality,email_domain,linkedin_activity,scam_reports,job_platform,salary_realism,
        upfront_payment,description_quality,interview_process,comm_channels,has_company_logo,"Has Questions",
        social_media,employee_reviews,physical_address,epf_registration,fssai_license,sebi_approval,
        description,fraudulent
    ]
    rows.append(row)

# header must match train_model expectations (we included many columns)
header = [
    "mca_registration","gstin","cin","iso_certification","pan_number","tan_number",
    "msme_registration","shop_license","import_export_code","professional_tax","website_quality",
    "domain_age","ssl_certificate","linkedin_profile","glassdoor_reviews","employee_count","turnover",
    "contact_number","office_address","epf_registration","website_quality_dup","email_domain","linkedin_activity",
    "scam_reports","job_platform","salary_realism","upfront_payment","description_quality","interview_process",
    "comm_channels","has_company_logo","has_questions","social_media","employee_reviews","physical_address",
    "epf_registration_dup","fssai_license","sebi_approval","description","fraudulent"
]

df = pd.DataFrame(rows, columns=header)
df.to_csv("job_data.csv", index=False)
print("Generated job_data.csv with", len(df), "rows")
