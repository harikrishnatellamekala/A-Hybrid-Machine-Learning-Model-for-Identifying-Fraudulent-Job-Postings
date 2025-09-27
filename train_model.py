# train_model.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

# NOTE: dataset filename must be job_data.csv
df = pd.read_csv("job_data.csv")

# Clean
df.fillna('', inplace=True)

# combine text fields (make sure these columns exist in job_data.csv)
text_cols = [
    "mca_registration","gstin","website_quality","email_domain","linkedin_activity",
    "scam_reports","job_platform","salary_realism","upfront_payment","description_quality",
    "interview_process","comm_channels","has_company_logo","has_questions","social_media",
    "employee_reviews","physical_address","epf_registration","fssai_license","sebi_approval",
    "description"
]

missing_cols = [col for col in text_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"Missing columns in CSV: {missing_cols}")

df["text"] = df[text_cols].astype(str).agg(" ".join, axis=1)
X = df["text"]
y = df["fraudulent"].astype(int)

vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X_vect = vectorizer.fit_transform(X)
joblib.dump(vectorizer, "vectorizer.pkl")

X_train, X_test, y_train, y_test = train_test_split(X_vect, y, test_size=0.2, random_state=42, stratify=y)

# Random Forest
rf = RandomForestClassifier(n_estimators=200, random_state=42)
rf.fit(X_train, y_train)
print("Random Forest Accuracy:", accuracy_score(y_test, rf.predict(X_test)))
joblib.dump(rf, "model_rf.pkl")

# Naive Bayes
nb = MultinomialNB()
nb.fit(X_train, y_train)
print("Naive Bayes Accuracy:", accuracy_score(y_test, nb.predict(X_test)))
joblib.dump(nb, "model_nb.pkl")

# SVM
svm = SVC(probability=True, kernel='linear')
svm.fit(X_train, y_train)
print("SVM Accuracy:", accuracy_score(y_test, svm.predict(X_test)))
joblib.dump(svm, "model_svm.pkl")

# XGBoost
xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', n_estimators=100)
xgb.fit(X_train, y_train)
print("XGBoost Accuracy:", accuracy_score(y_test, xgb.predict(X_test)))
joblib.dump(xgb, "model_xgb.pkl")

print("\n✅ Training Complete. Models + vectorizer saved successfully!")
