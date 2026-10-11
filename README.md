<p align="center">
  <img src="brand/skillher-logo.svg" alt="SkillHer" height="40">
</p>

<p align="center">
  <strong>Learn the skill. Land the opportunity.</strong><br>
  An AI-powered skill assessment and learning-path platform for women.
</p>

---

## Overview

**SkillHer** is a minimal, typography-led web platform designed to benchmark technical and professional proficiencies and generate actionable, milestone-driven learning roadmaps. It combines fast Groq LLM inference for adaptive question generation and curriculum synthesis with strict, deterministic backend link builders that prevent LLM URL hallucinations.

### Key Capabilities
- **Dynamic Per-Skill Assessments**: Enter any technical or professional skill (e.g. Data Analysis, React, UI Design, Public Speaking) to receive an 8–10 question adaptive assessment with server-side objective scoring.
- **Actionable 4 or 12-Week Roadmaps**: Weekly concrete deliverables calibrated to your available hours, complete with interactive progress checkboxes and a clean printable view (print CSS).
- **Deterministic Link Integrity**: All learning resources (YouTube tutorials, top GitHub repositories, internship search queries, free docs, communities, and certifications) are constructed deterministically with URL-encoding on the backend.
- **Ultra-Minimal UI (< 8 KB CSS, < 3 KB JS)**: Monochrome design language, system font stack, automatic dark mode via `prefers-color-scheme`, zero frontend frameworks, and full keyboard/screen-reader accessibility.
- **Serverless-Ready Architecture**: Runs natively on Vercel (`@vercel/python`) with WhiteNoise static asset compression.

---

## Environment Variables

Configure these variables in your `.env` file locally or in **Vercel Project Settings > Environment Variables**:

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | **Yes** | — | Django cryptographic secret key |
| `DEBUG` | No | `False` | Enable/disable debug mode (`True` for local development) |
| `GROQ_API_KEY` | **Yes** | — | Groq Cloud API key for AI question and roadmap generation |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Supported Groq model (e.g., `llama-3.3-70b-versatile` or `llama-3.1-8b-instant`) |
| `YOUTUBE_API_KEY` | No | — | Optional YouTube Data API v3 key for live top video results (falls back to search queries) |
| `GITHUB_TOKEN` | No | — | Optional GitHub personal access token for higher rate limits on repository lookups |
| `DATABASE_URL` | No | SQLite | Optional hosted PostgreSQL connection string (e.g. Neon, Supabase) |
| `CONTACT_EMAIL` | No | `malthumkarvarun@gmail.com` | Destination inbox for contact form submissions |
| `SMTP_HOST` | No | `smtp.gmail.com` | Outgoing SMTP host for email delivery |
| `SMTP_PORT` | No | `587` | Outgoing SMTP port (TLS) |
| `SMTP_USER` | No | — | SMTP user credentials |
| `SMTP_PASS` | No | — | SMTP app password |

See [.env.example](file:///.env.example) for a ready-to-use template.

### Secrets & Security
- **Never Commit Secrets**: Real `.env` and `.env.local` files must never be tracked or committed to version control.
- **Use Placeholders in Examples**: `.env.example` must contain purely illustrative placeholders (e.g. `your_groq_api_key_here`).
- **Secret Rotation**: If any credential is ever exposed or leaked into a public or shared space, rotate and invalidate it immediately at the respective provider console (Groq, Google Cloud, GitHub, Google App Passwords, Neon). Update the rotated secret in your local `.env` and in Vercel Project Settings.

---

## Local Development Setup

### 1. Clone & Navigate
```bash
git clone https://github.com/varun05126/llm_working.git
cd llm_working/skill_recommender
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and configure your keys:
```bash
cp .env.example .env
```

### 4. Run Migrations & Collect Static Files
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. Run the Development Server
```bash
python manage.py runserver
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Running Automated Tests

Run the full automated test suite (including schema validation, scoring engine, link builders, static assets, and mocked LLM flows):
```bash
python manage.py test
```

---

## Vercel Deployment

SkillHer is preconfigured for zero-configuration deployment on Vercel using `vercel.json` and `@vercel/python`:

1. Import the repository into your Vercel Dashboard.
2. In **Project Settings > Root Directory**, select `skill_recommender`.
3. Set your production environment variables (`GROQ_API_KEY`, `SECRET_KEY`, `GROQ_MODEL`, and optionally `DATABASE_URL`).
4. Click **Deploy**.

> [!NOTE]
> **Ephemeral SQLite Limitation**: On serverless platforms like Vercel, the local filesystem is ephemeral and read-only outside `/tmp/`. By default, SkillHer gracefully falls back to `/tmp/db.sqlite3` in serverless environments. For persistent production user accounts and saved roadmaps across invocations, configure a managed PostgreSQL database via the `DATABASE_URL` environment variable (e.g., Neon or Supabase).

---

## Architecture & Code Structure

```text
skill_recommender/
├── brand/                    # Master SVG brand assets (skillher-logo.svg, skillher-icon.svg)
├── static/
│   ├── css/app.css          # Single hand-written stylesheet (< 8 KB, dark mode, print CSS)
│   ├── js/app.js            # Progressive enhancement (< 3 KB vanilla JS)
│   └── img/                 # SVG assets served statically
├── templates/recommender/    # Semantic templates extending minimal base.html
├── recommender/
│   ├── services/
│   │   ├── llm.py           # Groq API client with timeouts, retries, and strict JSON parsing
│   │   ├── assessment.py    # Dynamic question generation, validation, and server-side scoring
│   │   ├── recommendations.py # 4/12-week roadmap synthesis, projects, and portfolio tips
│   │   └── links.py         # Deterministic URL builders (YouTube, GitHub, Jobs, Courses, Docs)
│   ├── models.py            # Assessment, AssessmentQuestion, AssessmentAnswer, Recommendation
│   ├── views.py             # Thin controller views
│   └── tests.py             # Comprehensive automated test suite
├── vercel.json              # Vercel serverless function configuration
└── requirements.txt         # Minimal Python dependencies (Django, requests, whitenoise, etc.)
```

---

## License

Developed with care for women empowerment and career advancement. Licensed under the [MIT License](LICENSE).  
Maintainer: [Varun Malthumkar](mailto:malthumkarvarun@gmail.com)