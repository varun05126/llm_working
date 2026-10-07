# 🌸 SkillHer — AI-Powered Skill Development & Career Roadmap Platform

[![Live Deployment](https://img.shields.io/badge/Production-Live%20on%20Vercel-success?style=for-the-badge&logo=vercel)](https://skillrecommender.vercel.app/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Groq AI](https://img.shields.io/badge/Groq%20AI-Llama%203-f55036?style=for-the-badge)](https://groq.com/)
[![Nodemailer](https://img.shields.io/badge/Mailer-Dual--Engine%20TLS-6366f1?style=for-the-badge)](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/mailer.js)

**SkillHer** is an intelligent career acceleration platform tailored for women in technology, leadership, and engineering. It analyzes user skill profiles, evaluates competencies via interactive assessments, and generates structured 3-month growth roadmaps powered by **Groq LLM** with deterministic real-time fallbacks.

🌐 **Live Website**: [https://skillrecommender.vercel.app/](https://skillrecommender.vercel.app/)  
📬 **Contact**: [malthumkarvarun@gmail.com](mailto:malthumkarvarun@gmail.com)

---

## ✨ Key Features

- **🎯 Skill Assessment Engine**: Interactive quizzes across technical domains, soft skills, and leadership to identify proficiency benchmarks.
- **⚡ Real-Time AI Roadmaps**: Custom 3-month actionable learning paths powered by Groq's high-speed LLM inference, with instant domain synthesis across 8 key tracks.
- **🛡️ Multi-Tier AI Guardrails Engine**:
  - **Rate Limiting**: Sliding-window IP rate limiter (30 req / 60s) preventing automated spam and abuse.
  - **Input Sanitization**: Cleanses non-printable control characters, null bytes, and enforces maximum character bounds.
  - **Heuristic Pattern Defense**: Zero-latency regex detection against jailbreaks, system overrides (`DAN`, roleplay bypasses), and malicious exploits.
  - **Meta Llama-Prompt-Guard-2-86M**: Real-time semantic injection probability analysis via Groq Cloud (`threshold > 0.85`).
  - **Output Moderation & Redaction**: Automatic scrubbing of sensitive API keys (`gsk_...`) and security credentials.
  - **Aria Persona Deflection**: Graceful, brand-aligned redirects maintaining professional career mentorship tone.
- **💬 Aria • AI Career Mentor Chatbot**: Floating, responsive AI coach with contextual career guidance, mock interviews, and portfolio strategies.
- **📄 1-Click High-Res PDF Export**: Client-side vectorized PDF export for customized 3-month blueprints.
- **🔄 Interactive Progress Tracker**: Live skill status tracking (Not Started, In Progress, Completed) with automatic completion percentages.
- **📬 Dual-Engine Email Dispatcher**:
  - **Local / Container**: Node.js & Nodemailer (`mailer.js`).
  - **Vercel Serverless**: Native Python TLS `smtplib` with automatic Google App Password sanitization.
- **🎨 Modern Responsive UI**:
  - Theme switcher with Dark, Light, and Cyber-Purple modes.
  - Fully mobile-optimized responsive navigation and card layouts.
  - Glassmorphic panels, gradient badges, and micro-animations.
- **📚 Curated Learning Library**: Filterable database of tutorials, courses, books, and certifications categorized by domain and level.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12, Django 5.x, WhiteNoise |
| **Frontend** | Vanilla CSS3, Bootstrap 5.3, FontAwesome 6, Google Fonts (Outfit / Inter) |
| **AI / Inference** | Groq Cloud API (Llama 3 / Mixtral) |
| **Email Engines** | Python `smtplib` (TLS), Nodemailer (Node.js) |
| **Hosting & CI/CD** | Vercel Serverless (`@vercel/python`), GitHub Actions |
| **Testing** | Django `TestCase`, Mock, Integration Test Suite |

---

## 🚀 Quick Start & Local Setup

### 1. Clone & Navigate
```bash
git clone https://github.com/varun05126/llm_working.git
cd skill_recommender
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Optional: Install Node Dependencies (For Nodemailer)
```bash
npm install
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
# AI API
GROQ_API_KEY=your_groq_api_key_here

# Django Security
SECRET_KEY=your_django_secret_key_here
DEBUG=True

# Email Delivery Configuration
CONTACT_EMAIL=malthumkarvarun@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=malthumkarvarun@gmail.com
SMTP_PASS=your_google_app_password
```

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests

Run the full automated unit and integration test suite:
```bash
python manage.py test
```
**Test Coverage Includes:**
- Public route availability (`home`, `about`, `contact`, `resources`).
- Authenticated vs unauthenticated permissions.
- Contact form submissions and database logging (`ContactMessage`).
- Dual-engine email dispatching and error handling.
- AJAX JSON API endpoints (`/api/contact/`).

---

## ☁️ Vercel Deployment

The project is configured for one-click Vercel serverless deployment using `vercel.json`:
- **Builder**: `@vercel/python` routing through `skill_recommender/wsgi.py`.
- **Static Assets**: Served via `WhiteNoiseMiddleware`.
- **CSRF Protection**: Preconfigured for HTTPS wildcard subdomains (`https://*.vercel.app`).

### Production Environment Variables in Vercel:
Add the following in **Project Settings > Environment Variables**:
- `GROQ_API_KEY`: Groq inference API key.
- `CONTACT_EMAIL`: Recipient inbox (`malthumkarvarun@gmail.com`).
- `SMTP_HOST`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `SMTP_USER`: Gmail address.
- `SMTP_PASS`: 16-character Google App Password.

---

## 📄 License & Credits

- Developed with ❤️ for women empowerment and career advancement.
- Licensed under the [MIT License](LICENSE).
- Maintainer: [Varun Malthumkar](mailto:malthumkarvarun@gmail.com).