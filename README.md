# A-Hybrid-Machine-Learning-Model-for-Identifying-Fraudulent-Job-Postings
# FakeJobDetector 🔍

A professional web application to detect **fake job postings** using NLP + ML models.  
Users can **register/login**, upload a job description (via **link, image, or plain text**) and run multiple algorithms (Naive Bayes, Random Forest, XGBoost, SVM) to check if the job is genuine, moderate, or fake.

---

## ✨ Features
- 👤 **User Authentication** (Register/Login/Logout) with SQLite3
- 🎯 **3 Input Modes**:
  - Job Posting Link
  - Job Posting Image (OCR using Tesseract)
  - Raw Text Description
- 🔑 **Keyword Matching**: Checks if job contains minimum required fields (developer, salary, location, etc.)
- 🧠 **ML Models Integration**:
  - Naive Bayes
  - Random Forest
  - XGBoost
  - Support Vector Machine
- ✅ **Conditional Buttons**:
  - Show ML prediction buttons **only if description is genuine** (matches > 3 keywords).
  - If not genuine → only show count and warning message.
- 🖥️ **Frontend Pages**:
  - Landing Page (quote + login/register prompt)
  - Dashboard (main tool after login)
  - About Us
  - Contact Us (with email + LinkedIn)

---

## 🛠️ Tech Stack
- **Backend:** Flask (Python)
- **Database:** SQLite3 (for user accounts)
- **ML Models:** scikit-learn, joblib
- **Frontend:** HTML + CSS (custom)
- **OCR:** Tesseract + pytesseract
- **Other libs:** pandas, requests, BeautifulSoup

---

## 📂 Project Structure
fakejob_site/
├── app.py # Flask app (auth + routes + ML integration)
├── utils.py # Utilities (OCR, scraping, keyword check)
├── requirements.txt # Python dependencies
├── users.db # Auto-created SQLite DB
├── uploaded_data.csv # Saved job descriptions (after genuine check)
├── vectorizer.pkl # Pre-trained vectorizer
├── model_nb.pkl # Naive Bayes model
├── model_rf.pkl # Random Forest model
├── model_xgb.pkl # XGBoost model
├── model_svm.pkl # SVM model
├── uploads/ # Uploaded images
├── static/
│ └── styles.css # Stylesheet
└── templates/
├── base.html
├── landing.html
├── register.html
├── login.html
├── index.html
├── result.html
├── algorithm_result.html
├── about.html
└── contact.html

yaml
Copy code

---

## ⚡ Setup & Installation

### 1. Clone or download project
```bash
git clone https://github.com/YOUR-USERNAME/fakejobdetector.git
cd fakejobdetector
2. Create virtual environment (optional but recommended)
bash
Copy code
python -m venv venv
Activate it:

Windows:

bash
Copy code
venv\Scripts\activate
Linux / macOS:

bash
Copy code
source venv/bin/activate
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Install Tesseract OCR
Windows: Download installer and install.

Linux (Debian/Ubuntu):

bash
Copy code
sudo apt-get install tesseract-ocr -y
macOS (brew):

bash
Copy code
brew install tesseract
5. Run the app
bash
Copy code
python app.py
6. Open in browser
Go to:
👉 http://127.0.0.1:5000

🚀 Usage
Landing Page

Shows inspirational quote & prompt to login/register.

Register/Login

New users register → login to access dashboard.

Dashboard

Submit job posting by Link, Image, or Text.

If not genuine: shows only match count + warning message.

If genuine: saves description, shows 4 ML algorithm buttons.

ML Prediction

Choose one algorithm (Naive Bayes, RF, XGBoost, SVM).

Shows prediction: Fake / Moderate / Genuine with confidence %.

If Moderate → suggests extra manual verification steps.

About Us

Shows project creator details & reason for building.

Contact Us

Shows email & LinkedIn link
