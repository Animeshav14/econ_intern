# 🎓 Internship GPT – AI-Powered Internship Finder

An AI-powered web application built with **Streamlit** and **OpenAI** that helps students find internships tailored to their **major, graduation year, preferred industry, and location**. The app connects to a **Google Sheets database** and interacts with users in a chatbot-style interface, making internship discovery simple and personalized.

---

## 🚀 Features

- 🤖 **AI Assistant** – A chatbot that asks users questions and recommends relevant internships.
- 📊 **Google Sheets Integration** – Internship listings are dynamically loaded from multiple sheets.
- 🔎 **Smart Filtering** – Search by major, graduation year, industry, and optional location.
- 📝 **Resume Feedback** – Paste your resume text to get feedback on your fit for positions.
- 🔗 **Clickable Results** – Internship titles link directly to the application page.
- 🖼️ **Custom Branding** – Add your club logo to personalize the interface.

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Streamlit** – UI and deployment
- **OpenAI API** – GPT-powered recommendations
- **Pandas** – Data handling and filtering
- **Google Sheets (CSV Export)** – Internship data source
- **dotenv / Streamlit Secrets** – Secure environment variable management

---

## 📁 Project Structure

├─ app.py # Main Streamlit app
├─ utils/
│ ├─ gpt.py # Handles GPT API calls
│ └─ sheets.py # Loads and filters data
├─ assets/
│ └─ club_logo.png # Club logo (optional)
├─ requirements.txt # Python dependencies
├─ README.md # Documentation
└─ .gitignore # Ignored files (includes .env)


---

## ⚙️ Local Setup

1. **Clone the repo:**
```bash
git clone https://github.com/yourusername/internship-gpt.git
cd internship-gpt

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=o4-mini
INDUSTRY_LIST=Finance,Research
FINANCE_SHEET_CSV=https://docs.google.com/spreadsheets/.../export?format=csv&gid=0
RESEARCH_SHEET_CSV=https://docs.google.com/spreadsheets/.../export?format=csv&gid=1776427913

streamlit run app.py

☁️ Deploy on Streamlit Cloud

Push your project to GitHub.

Go to https://share.streamlit.io
.

Create a new app and select app.py as the main file.

In “Secrets”, paste your environment variables:

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=o4-mini
INDUSTRY_LIST=Finance,Research
FINANCE_SHEET_CSV=https://docs.google.com/spreadsheets/.../export?format=csv&gid=0
RESEARCH_SHEET_CSV=https://docs.google.com/spreadsheets/.../export?format=csv&gid=1776427913

https://your-username-internship-gpt.streamlit.app

🧠 Future Enhancements

Add more industries (consulting, data science, policy)

Include application deadlines and reminders

Enhance resume scoring and recommendations

Allow users to bookmark or save opportunities

🤝 Contributing

Contributions are welcome! Fork the repo, create a new branch, and open a pull request. If you’re part of the Economics Club, you can also contribute new internship data through Google Sheets.

📜 License

This project is licensed under the MIT License. You’re free to use, modify, and distribute it for academic or personal use.