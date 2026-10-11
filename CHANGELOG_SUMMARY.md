# Audit & Rebranding Report: SkillHer

**Audit Date**: October 11, 2026  
**Auditor**: Antigravity Assistant  
**Repository**: `https://github.com/varun05126/llm_working` (Branch: `main`, Base Commit: `8bdd1a4`)  
**Product**: **SkillHer** (Rebranded from *Women Skill Development Recommender*)

---

## UI REBUILD & EMPOWERMENT ANIMATIONS PASS (Stage 1)

**Pass Date**: October 11, 2026  
**Auditor**: Antigravity Assistant  
**Repository**: `https://github.com/varun05126/llm_working` (Branch: `main`)  
**Product**: **SkillHer**

### 1. Overview & Core Deliverables
- **Truly Full-Width Responsive Layout**: Header and footer span the full viewport width (edge-to-edge on 2380px/2560px displays) with `padding-inline: var(--gutter)`. Page content expanded from narrow column to fluid container `width: min(100% - 2 * var(--gutter), 1600px)` with `--gutter: clamp(1rem, 4vw, 4rem)`.
- **Home Page Rebuild**:
  - Two-column hero on >= 1024px with headline, rotating word set, buttons, and custom inline SVG line-art illustration.
  - "How SkillHer Works": 3-card auto-fit grid (`minmax(260px, 1fr)`) with subtle hover elevation.
  - "Supported Learning Domains": Responsive chip grid filling container width.
  - "Women Who Led the Way": 5 factual pioneer cards (Ada Lovelace, Grace Hopper, Katherine Johnson, Margaret Hamilton, Radia Perlman).
- **Subtle Empowerment Animations**:
  - Original inline SVG line-art illustration with animated rising steps, trajectory draw, floating woman figure, twinkling summit star and sparkles.
  - Rotating headline word set ("Learn", "Build", "Lead", "Grow") via CSS keyframes with `aria-label` for screen readers.
  - Scroll reveals via IntersectionObserver (Progressive enhancement; zero hidden content without JS).
  - Assessment wizard smooth question slide/fade and option selection pulse.
  - Results celebration: subtle canvas starburst (< 1 KB) running once per roadmap visit.
  - Milestone checkboxes with animated line-through and smooth progress fill.
  - Strict `@media (prefers-reduced-motion: reduce)` support disabling all motion.

### 2. Assets & Size Limits
- `static/css/app.css`: **23,885 bytes** (~23.9 KB) (Requirement: < 30 KB).
- `static/js/app.js`: **7,430 bytes** (~7.4 KB) (Requirement: < 8 KB).

### 3. Verification & Evidence
- **Playwright Automated Tests**: Tested and captured screenshots across 360px, 768px, 1280px, 1920px, and 2560px in both Light and Dark mode.
- **Horizontal Overflow**: `scrollWidth <= clientWidth` verified across all viewports (0 horizontal overflow).
- **No-JS Accessibility**: 100% of sections visible when JavaScript is disabled (12/12 reveal elements visible).
- **Reduced Motion**: All animations disabled when `prefers-reduced-motion: reduce` is enabled (`animation: none`).
- **Django Check**: `System check identified no issues (0 silenced)`.
- **Test Suite**: 21/21 passed (`DATABASE_URL=""`).
- **Unverified Scope**: Real physical iOS/Android device touch interaction and production Vercel edge deployment (waiting for Stage 2 approval).

---

## COMPREHENSIVE AUDIT REPORT: PRODUCTION BUGFIX & POLISH PASS

**Audit Date**: October 11, 2026  
**Auditor**: Antigravity Assistant  
**Repository**: `https://github.com/varun05126/llm_working` (Branch: `main`)  
**Product**: **SkillHer**

---

### 1. SUMMARY
- **Overview**: Resolved production URL routing and debug security risks, implemented an in-house zero-dependency XSS-safe markdown renderer, scrubbed LLM model names and placeholder titles, restructured the roadmap header with clean metadata cards, and expanded the layout into a fluid responsive grid with zero mobile blowout.
- **Status of Core Deliverables**:
  - **a) `/contact` 404 and the catch-all URL pattern**: **DONE**
  - **b) DEBUG default and the custom 404/500 pages**: **DONE**
  - **c) Markdown rendering of AI text**: **DONE**
  - **d) Roadmap page content cleanup (model name, tier label, skill/goal/hours fields)**: **DONE**
  - **e) Full-screen responsive layout**: **DONE**

---

### 2. FILES CHANGED
#### File Change Manifest
| File | Action | Rationale |
| :--- | :--- | :--- |
| `skill_recommender/urls.py` | Modified | Excised `static()` / `media()` serve patterns to ensure WhiteNoise solely serves static files. |
| `skill_recommender/settings.py` | Modified | Enforced `DEBUG = os.getenv("DEBUG", "False") == "True"` and explicitly set `APPEND_SLASH = True`. |
| `recommender/services/markdown_render.py` | Added | Zero-dependency markdown-to-HTML parser with HTML escaping, link whitelisting, and single-line repair. |
| `recommender/templatetags/markdown_tags.py` | Added | Registered `{{ value|render_md }}` template tag library. |
| `recommender/templatetags/recommender_tags.py` | Modified | Exposed `render_md` filter alongside legacy filters for backward compatibility. |
| `recommender/services/recommendations.py` | Modified | Guarded AI prompt against emitting model names or document headers; improved fallback structures. |
| `recommender/views.py` | Modified | Enriched roadmap context with normalized skill, goal, weekly hours, and tier metadata. |
| `recommender/tests.py` | Modified | Added 21 automated unit tests for redirects, XSS sanitization, markdown syntax, and single-line repair. |
| `static/css/app.css` | Modified | Full-screen responsive system (fluid container, clamp typography, 2-col desktop grid, mobile nav wrap). |
| `templates/404.html` | Added | Minimal monochrome root 404 error template extending `recommender/base.html`. |
| `templates/500.html` | Added | Minimal monochrome root 500 server error template extending `recommender/base.html`. |
| `templates/recommender/404.html` | Added | App-level 404 error fallback template matching SkillHer theme. |
| `templates/recommender/500.html` | Added | App-level 500 server error fallback template matching SkillHer theme. |
| `templates/recommender/recommendation_detail.html` | Modified | Applied `render_md` on all AI text, added 3-field metadata card, cleaned tier header. |
| `templates/recommender/recommendations.html` | Modified | Applied `render_md` filter to recommendation description cards. |
| `templates/recommender/profile.html` | Modified | Applied `render_md` filter to saved recommendation summaries. |
| `templates/recommender/skill_assessment.html` | Modified | Applied `render_md` filter to question explanations. |
| `templates/recommender/contact.html` | Modified | Responsive container and spacing adjustments. |
| `templates/recommender/login.html` | Modified | Constrained auth form card width to 480px centered. |
| `templates/recommender/register.html` | Modified | Constrained auth form card width to 480px centered. |

#### `git status`
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   recommender/services/recommendations.py
  modified:   recommender/templatetags/recommender_tags.py
  modified:   recommender/tests.py
  modified:   recommender/views.py
  modified:   skill_recommender/settings.py
  modified:   skill_recommender/urls.py
  modified:   static/css/app.css
  modified:   templates/recommender/contact.html
  modified:   templates/recommender/login.html
  modified:   templates/recommender/profile.html
  modified:   templates/recommender/recommendation_detail.html
  modified:   templates/recommender/recommendations.html
  modified:   templates/recommender/register.html
  modified:   templates/recommender/skill_assessment.html

Untracked files:
  recommender/services/markdown_render.py
  recommender/templatetags/markdown_tags.py
  templates/404.html
  templates/500.html
  templates/recommender/404.html
  templates/recommender/500.html

no changes added to commit (use "git add" and/or "git commit -a")
```

---

### 3. URL AND DEBUG FIX
#### Before & After: `skill_recommender/urls.py`
```diff
--- a/skill_recommender/urls.py
+++ b/skill_recommender/urls.py
@@ -1,14 +1,8 @@
 from django.contrib import admin
 from django.urls import path, include
-from django.conf import settings
-from django.conf.urls.static import static

 urlpatterns = [
     path('admin/', admin.site.urls),
     path('accounts/', include('django.contrib.auth.urls')),
     path('', include('recommender.urls')),
-]
-
-if settings.DEBUG:
-    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
-    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
+]
```

#### Settings & Status Codes
- **`APPEND_SLASH`**: Explicitly set to `True` in `settings.py`.
- **`DEBUG` Default Value**: `DEBUG = os.getenv("DEBUG", "False") == "True"` (defaults to `False` whenever unset or set to any value other than `"True"`).
- **Verified Status Codes (via Django Test Client)**:
  - `/contact` -> **301** (Redirects to `/contact/`) -> **200 OK**
  - `/about` -> **301** (Redirects to `/about/`) -> **200 OK**
  - `/login` -> **301** (Redirects to `/login/`) -> **200 OK**
  - `/non-existent-page-url/` -> **404 Not Found** (Custom `404.html` rendered)
- **Static Assets Loading (WhiteNoise)**:
  - `/static/css/app.css` -> **200 OK** (`WhiteNoiseFileResponse`)
  - `/static/img/skillher-logo.svg` -> **200 OK** (`WhiteNoiseFileResponse`)
  - `/static/img/skillher-icon.svg` -> **200 OK** (`WhiteNoiseFileResponse`)

---

### 4. MARKDOWN RENDERER
#### Implementation Details
- **Architecture**: Implemented in `recommender/services/markdown_render.py` using Python standard library only (`html`, `re`). Zero external packages.
- **Supported Syntax**:
  - Headings: `#`, `##`, `###`, `####` -> `<h1>`, `<h2>`, `<h3>`, `<h4>`
  - Inline Styling: `**bold**` -> `<strong>`, `*italic*` -> `<em>`, `` `code` `` -> `<code>`
  - Fenced Code Blocks: ```` ```lang ... ``` ```` -> `<pre><code>...</code></pre>`
  - Blockquotes: `> quote` -> `<blockquote>`
  - Lists: Ordered (`1. item`) -> `<ol><li>`, Unordered (`- item`, `* item`) -> `<ul><li>`
  - Horizontal Rules: `---` -> `<hr>`
  - Paragraphs: Standard lines grouped into `<p>`
- **HTML Escaping**: Every block of text is processed with `html.escape(text, quote=True)` prior to regex substitutions, neutralizing all raw HTML entities.
- **Link Security**: Only URLs with `http://` or `https://` schemas are transformed into hyperlinks (`<a href="..." target="_blank" rel="noopener noreferrer">`). Any invalid or malicious schema (`javascript:`, `data:`, `file:`) is converted into harmless text `[Text] (url)`.
- **Legacy Single-Line Record Repair**: Automatically injects newlines before mid-sentence heading and list tokens (`###`, `- `, `* `, `1. `) that were previously collapsed into single strings in legacy records.

#### XSS Test Verification
- **Test Case 1 (Script Injection)**:
  - Input: `<script>alert('pwn')</script>`
  - Rendered: `<p>&lt;script&gt;alert(&#x27;pwn&#x27;)&lt;/script&gt;</p>`
  - Result: **Passed**. Zero executable script tags.
- **Test Case 2 (JavaScript URL Scheme)**:
  - Input: `[Click me](javascript:alert(1))`
  - Rendered: `<p>Click me (javascript:alert(1))</p>`
  - Result: **Passed**. Scheme stripped; zero `href="javascript:..."` attributes.

#### Template Coverage
The `render_md` template filter is loaded and applied across all views displaying AI or dynamic content:
1. `templates/recommender/recommendation_detail.html`:
   - `{{ rec.description|render_md }}`
   - `{{ rec.project_ideas|render_md }}`
   - `{{ rec.resume_tips|render_md }}`
   - `{{ rec.interview_topics|render_md }}`
2. `templates/recommender/recommendations.html`:
   - `{{ rec.description|render_md }}`
3. `templates/recommender/profile.html`:
   - `{{ rec.description|render_md }}`
4. `templates/recommender/skill_assessment.html`:
   - `{{ question.explanation|render_md }}`

**Audit Confirmation**: No AI-generated text is output without the `render_md` filter.

#### Before / After Example (Real Recommendation #6 / #20)
**Input Raw Markdown**:
```markdown
### Milestone Overview
- **Week 1**: Core Deep-Dive & Conventions
- **Week 2**: Advanced Concurrency & AsyncIO
1. Build hands-on project
2. Write unit tests

Check out [Official Docs](https://docs.python.org/3/) for reference.
```

**Output Rendered HTML**:
```html
<h3>Milestone Overview</h3>
<ul>
<li><strong>Week 1</strong>: Core Deep-Dive & Conventions</li>
<li><strong>Week 2</strong>: Advanced Concurrency & AsyncIO</li>
</ul>
<ol>
<li>Build hands-on project</li>
<li>Write unit tests</li>
</ol>
<p>Check out <a href="https://docs.python.org/3/" rel="noopener noreferrer" target="_blank">Official Docs</a> for reference.</p>
```

---

### 5. CONTENT CLEANUP
#### Model Name Scrubbing
- **Grep Command**:
  ```bash
  grep -rn -i "qwen" recommender/ templates/ static/
  ```
- **Output**:
  ```
  recommender/tests.py:567:        text = "### Strategic AI Career Guidance (qwen/qwen3.8-27b):\nRoadmap overview."
  recommender/tests.py:570:        self.assertNotIn('qwen', out)
  recommender/services/markdown_render.py:15:    # "### Strategic AI Career Guidance (qwen/qwen3.8-27b):" or "(qwen/...)"
  recommender/services/markdown_render.py:27:        r'\((?:qwen|openai|llama|deepseek|groq)[^)]*\)',
  ```
- **Confirmation**: Zero model names appear anywhere in templates, views, or static files. The only references are the regex stripper and the automated test verifying its removal.

#### Roadmap Header Elements
- **Tier/Level Badge**: Dynamically renders assessed tier (`Beginner`, `Intermediate`, `Advanced`) paired with the skill name (e.g. `Intermediate Level • Python Roadmap`).
- **3-Field Parameter Card**: Replaced the previous awkward sentence with a clean structured grid card:
  - **Target Skill**: Clear skill name (e.g., `Python`).
  - **Career Goal**: Target job role (e.g., `Software Engineer`).
  - **Weekly Commitment**: Allocated study time (e.g., `8 hrs/week`).

---

### 6. RESPONSIVE LAYOUT
#### CSS Architecture (`static/css/app.css`)
- **Container Width**:
  ```css
  .container {
    width: min(100% - 2 * var(--gutter), 1400px);
    margin-inline: auto;
  }
  :root {
    --gutter: clamp(1rem, 4vw, 3rem);
  }
  ```
- **Fluid Typography**:
  - Base: `clamp(1rem, 0.95rem + 0.25vw, 1.125rem)`
  - H1: `clamp(2rem, 1.5rem + 2.5vw, 3.25rem)`
  - H2: `clamp(1.5rem, 1.25rem + 1.2vw, 2.25rem)`
  - H3: `clamp(1.2rem, 1.1rem + 0.6vw, 1.5rem)`
  - Prose reading limit: `max-width: 70ch;`
- **Breakpoints**:
  - Mobile (< 540px): Navigation flexes to column wrap; prevents horizontal expansion.
  - Desktop (>= 1024px): `.roadmap-grid` displays 2 columns (`minmax(0, 1fr) 340px`) with sticky milestone progress tracker (`position: sticky; top: var(--space-6)`).
  - Form Cards: Auth cards constrained to `480px`; Wizard card constrained to `720px`.

#### Viewport Verification (360px, 768px, 1024px, 1440px, 1920px)
- **Method**: Programmatically verified across viewports on a running Django LiveServer using Playwright headless Chromium.
- **Results**:
  - `360px`: `scrollWidth == clientWidth` (Horizontal Overflow: **False**)
  - `768px`: `scrollWidth == clientWidth` (Horizontal Overflow: **False**)
  - `1024px`: `scrollWidth == clientWidth` (Horizontal Overflow: **False**)
  - `1440px`: `scrollWidth == clientWidth` (Horizontal Overflow: **False**)
  - `1920px`: `scrollWidth == clientWidth` (Horizontal Overflow: **False**)
- **HONEST DECLARATION**: Verification was performed strictly via automated headless Chromium viewport measurement. The pages were **NOT inspected visually with human eyes** in an interactive graphical browser window.
- **New Size of `app.css`**: `13,441 bytes` (~13.4 KB).

---

### 7. TESTING
#### System Check & Automated Test Suite
- **Django Check**:
  ```bash
  ./venv/bin/python manage.py check
  ```
  **Output**: `System check identified no issues (0 silenced).` (Exit code: 0)
- **Full Test Suite**:
  ```bash
  DATABASE_URL="" ./venv/bin/python manage.py test
  ```
  **Output**:
  ```
  Found 21 test(s).
  Creating test database for alias 'default'...
  System check identified no issues (0 silenced).
  .....................
  ----------------------------------------------------------------------
  Ran 21 tests in 6.524s

  OK
  Destroying test database for alias 'default'...
  ```
  **Result**: **21 passed, 0 failed, 0 errors**.

#### What Was Verified vs. NOT Verified
- **Verified**:
  - All 21 Django unit tests (routing redirects, markdown rendering, XSS escaping, question set caching, assessment flow).
  - Trailing slash 301 redirects to `/contact/`, `/about/`, `/login/`.
  - WhiteNoise static asset delivery (HTTP 200).
  - DOM scroll width vs. client width across 5 viewports via Playwright.
- **NOT Verified**:
  - Human visual layout review in a real desktop/mobile browser.
  - Production deployment on Vercel edge infrastructure (pending user push).
  - Remote production database data migration (unnecessary, but unverified on remote server).

---

### 8. DEPLOYMENT STEPS FOR YOU
Follow these exact steps to deploy to production:

1. **Commit and Push Changes**:
   ```bash
   git add recommender/ skill_recommender/ static/ templates/ CHANGELOG_SUMMARY.md
   git commit -m "fix(prod): resolve /contact routing, debug leak, markdown rendering, and responsive grid"
   git push origin main
   ```
2. **Configure Environment Variables in Vercel**:
   - Go to: Vercel Dashboard -> Your Project -> Settings -> Environment Variables.
   - Variable `DEBUG`: Set to `False` (or remove it completely so it defaults to `False`).
3. **Trigger Production Redeploy**:
   - Automatic: Pushing to `main` triggers a Vercel deployment.
   - Manual (CLI): Run `vercel --prod` if manual deployment is preferred.
4. **Database Migration & Data-Fix Commands**:
   - **No manual database migration or data-fix commands are required.**
   - The `render_md` filter converts existing saved roadmaps dynamically at template render time. Historical records in production PostgreSQL will immediately render with clean formatting without altering database rows.

---

### 9. KNOWN ISSUES AND RISKS
1. **Tables in Markdown**: The zero-dependency markdown parser supports headings, lists, bold/italics, quotes, and code blocks, but does not parse markdown table syntax (`| col | col |`). If the LLM generates a markdown table, it will render as formatted paragraph text.
2. **Deeply Nested Lists**: Lists nested beyond 1 level are flattened into single-level lists.
3. **Continuous Unbroken Strings**: While `overflow-wrap: break-word` is enabled, single strings exceeding 1000 uninterrupted characters could expand inline parent elements on narrow viewports.
4. **Neon Postgres Test DB Contention**: Running `python manage.py test` against a remote Neon PostgreSQL connection pooler can hang during `DROP DATABASE test_neondb`. Always run local tests with `DATABASE_URL=""` using SQLite.

---

### 10. NEXT STEPS (Priority Order)
1. **Milestone Checkbox Persistence**: Add an AJAX/fetch endpoint to save milestone checkbox states (`completed_milestones` field on `Recommendation`) so user progress persists across sessions.
2. **Download / Export Roadmap**: Implement a clean printable stylesheet or PDF export for offline learning.
3. **Markdown Table Parsing**: Add a lightweight table parser in `markdown_render.py` to support multi-column curriculum schedules.
4. **Synthetic Production Health Check**: Create a lightweight `/healthz` endpoint monitored by an uptime service to detect Vercel serverless cold-start failures.
5. **Production Password Reset Flow**: Configure SMTP variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`) in Vercel and customize Django password reset email templates.

---
---

## PRE-DEPLOYMENT HARDENING PASS (Vercel & Security Hardening)
**Audit Date**: October 11, 2026  
**Auditor**: Antigravity Assistant

### 1. What Was Found (Audit & Root Cause Analysis)
- **Commit `29701c7` (`feat: add environment template and initial design plan`)**: Committed real credentials into `.env.example`:
  - `YOUTUBE_API_KEY`: Real Google Cloud API key (`AIza` prefix).
  - `SMTP_PASS`: Real 16-character Gmail App Password.
  - `SMTP_USER` & `CONTACT_EMAIL`: Real personal Gmail address.
- **Git History Scan (`git log --all --full-history`)**:
  - Files named `.env` and `.env.local` were **never committed** to git history (only `.env.example` was tracked).
  - Secret patterns (Groq prefix, Google API prefix, `SMTP_PASS`) existed exclusively in commit `29701c7` and mock test fixtures.
- **Local Environment Review**:
  - `manage.py test` against remote `DATABASE_URL` attempted to create a test database on Neon. Tests must run with `DATABASE_URL=""` to isolate local testing from production databases.

### 2. Mandatory Credential Rotation Checklist
Even if git history is scrubbed, any credential pushed to a public/remote repository must be treated as compromised. Rotate immediately:
1. **Google Gmail App Password**:
   - Location: Google Account -> Security -> 2-Step Verification -> App passwords.
   - Action: Revoke the existing 16-letter app password and generate a new one.
2. **Google Cloud YouTube API Key**:
   - Location: [console.cloud.google.com](https://console.cloud.google.com) -> APIs & Services -> Credentials.
   - Action: Delete the exposed API key; create a new key and restrict it to YouTube Data API v3 and HTTP referrers.
3. **Groq API Key**:
   - Location: [console.groq.com](https://console.groq.com) -> API Keys.
   - Action: Revoke existing key and generate a fresh key.
4. **Hosted PostgreSQL Database Password (Neon / Supabase)**:
   - Location: Neon Dashboard -> Project Settings / Role Passwords.
   - Action: Reset database password if it was ever placed into any tracked file.
5. **Django SECRET_KEY**:
   - Location: Vercel Project Settings -> Environment Variables -> `SECRET_KEY`.
   - Action: Generate a fresh 50-character random cryptographic secret for production.

### 3. Git History Scrubbing Commands & Trade-offs
To purge commit `29701c7` or `.env.example` historical diffs from git history:

#### Option A: Using `git-filter-repo` (Recommended)
```bash
# 1. Install git-filter-repo
brew install git-filter-repo

# 2. Scrub .env.example from past commit history
git filter-repo --path .env.example --invert-paths
```

#### Option B: Using BFG Repo-Cleaner
```bash
# 1. Place credentials to purge in passwords.txt (one per line)
# 2. Run BFG
bfg --replace-text passwords.txt
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

#### Critical Trade-offs & Rules:
- **Rewrites Commit Hashes**: History rewriting changes the SHA-1 hash of every commit downstream of `29701c7`.
- **Requires Force-Push**: Pushing the scrubbed history requires `git push origin --force --all`. Any collaborator working on branches will encounter detached heads and diverged trees.
- **Rotation is Mandatory Regardless**: GitHub scrapers and bot indexers scan commits in real time. **Scrubbing history does not un-compromise an exposed secret.** Rotation remains strictly required.
- **Approval Gate**: In accordance with global rules, Antigravity will NOT execute history rewriting or `git push --force` without explicit approval.

### 4. What Changed in This Hardening Pass
1. **Sanitized `.env.example`**:
   - Replaced all credentials with generic placeholders (`your_groq_api_key_here`, `your_email@gmail.com`, etc.).
   - Added complete parameter list: `SECRET_KEY`, `DEBUG`, `GROQ_API_KEY`, `GROQ_MODEL`, `YOUTUBE_API_KEY`, `GITHUB_TOKEN`, `DATABASE_URL`, `CONTACT_EMAIL`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`.
2. **Hardened `.gitignore`**:
   - Explicitly ignores `.env`, `.env.*`, `.env.local`, `*.sqlite3`, `staticfiles/`, `venv/`, `__pycache__/`, while preserving `!.env.example`.
3. **Automated Pre-Commit Security Hook (`.git/hooks/pre-commit`)**:
   - Shell script blocking commits if staged files contain live API key patterns or files named `.env` / `.env.local`. Prints clean warning without leaking the matched value.
4. **Documentation**:
   - Added dedicated "Secrets & Security" subsection to `README.md`.
5. **Serverless Settings & WSGI Hardening**:
   - `DEBUG`: Defaults to `False` in serverless/production (`VERCEL=1`), `True` in local development.
   - Startup warning logger in `settings.py`: Emits clear non-sensitive warnings for missing `SECRET_KEY`, `GROQ_API_KEY`, and unconfigured `DATABASE_URL` in serverless.
   - `skill_recommender/wsgi.py`: Protected against cold-start concurrency table lock contention on production Postgres; `migrate` is only executed dynamically for ephemeral local `/tmp/db.sqlite3`.
6. **7-Day Database Question Set Caching**:
   - Added `AssessmentQuestionCache` model (`normalized_skill`, `normalized_goal`, `questions_data`, `created_at`).
   - `generate_skill_questions` queries the database cache before calling Groq, eliminating duplicate LLM API calls and cost for repeat skills within 7 days.
   - Created migration `recommender/migrations/0005_assessmentquestioncache.py`.
   - Added `QuestionCachingTestCase` in `recommender/tests.py`.
7. **URL Encoding Verification**:
   - Verified that `urllib.parse.quote_plus` encodes tricky skills like `C++` (`C%2B%2B`), `C#` (`C%23`), and `Data Analysis` (`Data+Analysis`) without breaking URLs.
8. **Automated Test Suite**:
   - All 12 automated unit and integration tests passing (`12 passed, 0 failed`).

### 5. Production Database Migrations on Vercel
Vercel's serverless runtime does not automatically run `python manage.py migrate`.
- **Trade-off Summary (3 Lines)**:
  - *One-time manual CLI migration*: Safest option, avoids cold-start latency, eliminates database lock race conditions across lambdas, and prevents build timeouts.
  - *Build step in Vercel (`builds`)*: Exposes production database credentials to build workers and fails if database connections are rate-limited during deployment.
  - *Cold-start WSGI execution*: Dangerous; concurrent serverless container scaling leads to deadlock table collisions on PostgreSQL.
- **Exact Command to Run Manually**:
  Run this one-time command from your terminal against your hosted PostgreSQL instance (e.g. Neon):
  ```bash
  DATABASE_URL="postgres://<user>:<password>@<neon-host>/<dbname>?sslmode=require" ./venv/bin/python manage.py migrate
  ```

### 6. Exact Manual Deployment & Redeploy Steps
1. In Vercel Project Settings -> **Environment Variables**, set:
   - `SECRET_KEY` = (newly generated key)
   - `DEBUG` = `False`
   - `GROQ_API_KEY` = (newly generated Groq key)
   - `GROQ_MODEL` = `llama-3.3-70b-versatile`
   - `DATABASE_URL` = (production PostgreSQL connection string)
   - `YOUTUBE_API_KEY` = (optional new restricted key)
   - `GITHUB_TOKEN` = (optional GitHub personal access token)
   - `CONTACT_EMAIL` = (your contact email)
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` = (newly generated app credentials)
2. **Vercel Root Directory**:
   - Confirm Root Directory is `./` (default repository root, where `manage.py` and `vercel.json` live).
3. **Trigger Redeploy**:
   - In Vercel dashboard: Deployments -> Redeploy -> Without Build Cache.

### 7. Unverified / Pending Items
- **Actual Network Email Dispatch**: Tested pure Python TLS dispatcher locally; live delivery to Google SMTP servers requires updated valid app password.
- **Live Groq LLM Inference**: Tested unmocked call; local key lacked model tier permission for `llama-3.3-70b-versatile`, confirming successful fallback path. Requires valid upgraded/configured key on Vercel.
- **Remote Neon Migration**: Pending manual developer execution of the `manage.py migrate` command above.

---

## 1. OVERVIEW

### 5-Line Summary
1. The platform was completely rebranded from "Women Skill Development Recommender" to **SkillHer**, an AI-powered skill assessment and learning-path platform for women.
2. All Node/npm dependencies (`package.json`, `package-lock.json`, `node_modules`, `mailer.js`), Bootstrap 5, FontAwesome, Google Fonts, and external CDN dependencies were excised from the codebase.
3. A typography-led monochrome UI was implemented using a single hand-written CSS stylesheet ([static/css/app.css](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/static/css/app.css): 8.8 KB) and progressive vanilla JS ([static/js/app.js](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/static/js/app.js): 4.4 KB) with automatic dark mode.
4. The assessment engine was re-engineered to be dynamically skill-specific (accepting any free-text skill) with structured Groq LLM question generation, server-side objective scoring, and curated offline fallbacks.
5. The recommendation engine now generates personalized 4- or 12-week roadmaps paired with strict deterministic link builders (YouTube, GitHub, Internships, Docs, Communities, Certifications) preventing LLM URL hallucinations.

### Phases Completed
- **Phase A**: Dependency and CDN cleanup; brand SVG generation; minimal monochrome UI design system (`app.css`, `app.js`); template base redesign.
- **Phase B**: Dynamic skill assessment engine; structured JSON schemas; server-side scoring algorithms; `Assessment`, `AssessmentQuestion`, and `AssessmentAnswer` models and migrations.
- **Phase C**: Recommendation roadmap synthesizer; deterministic URL builders for YouTube, GitHub, internships, courses, and communities; 24-hour API caching.
- **Phase D**: Extra features: interactive milestone progress checkboxes (`api_toggle_milestone`), re-assess flows, printable roadmap CSS (`@media print`), portfolio/interview prep advice.
- **Phase E**: Pure Python TLS email dispatcher (`smtplib`); 11-test automated suite; comprehensive documentation ([README.md](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/README.md), [.env.example](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/.env.example)).

---

## 2. FILES

### File Modifications & Status (relative to `skill_recommender/`)

#### Root Configuration & Documentation
- `modified:   .gitignore`: Removed `node_modules/` reference; unignored `!.env.example`.
- `modified:   README.md`: Consolidated obsolete documentation into a single guide with SkillHer branding, setup, architecture, and deployment instructions.
- `added:      .env.example`: Template for required and optional environment variables.
- `added:      PLAN.md`: Initial design and execution plan.
- `deleted:    package.json`: Excised Node.js build config.
- `deleted:    package-lock.json`: Excised npm lockfile.
- `deleted:    mailer.js`: Excised Node.js Nodemailer script.

#### Brand & Static Assets
- `added:      brand/skillher-icon.svg`: Master 64x64 vector icon of woman with hair bun studying over open book.
- `added:      brand/skillher-logo.svg`: Master 250x64 vector logo pairing icon and wordmark with `prefers-color-scheme` support.
- `added:      static/img/skillher-icon.svg`: Statically served icon copy.
- `added:      static/img/skillher-logo.svg`: Statically served logo copy.
- `added:      static/css/app.css`: Single hand-written stylesheet (8.8 KB) providing CSS custom properties, system font stack, dark mode, and print styles.
- `added:      static/js/app.js`: Vanilla JS progressive enhancement (4.4 KB) for question wizard steps, rating buttons, loading spinners, and progress checks.
- `deleted:    static/css/style.css`: Excised old 34 KB Bootstrap-dependent stylesheet.

#### Services Architecture
- `added:      recommender/services/__init__.py`: Services package module.
- `added:      recommender/services/llm.py`: Groq Cloud client with timeouts, configurable model (`GROQ_MODEL`), retries, and JSON extractor.
- `added:      recommender/services/assessment.py`: Dynamic question generator, schema validator, curated offline banks, and server-side scoring.
- `added:      recommender/services/links.py`: Deterministic URL builders for YouTube, GitHub, internships, courses, and communities with 24-hour cache.
- `added:      recommender/services/recommendations.py`: Roadmap synthesizer, project generator, interview/resume advisor, and link enricher.

#### Django App Core
- `modified:   recommender/models.py`: Added `Assessment`, `AssessmentAnswer`, enhanced `AssessmentQuestion` and `Recommendation` with JSONFields.
- `added:      recommender/migrations/0004_alter_assessmentquestion_options_and_more.py`: Migration applying new and updated models.
- `modified:   recommender/urls.py`: Updated routes for assessment wizard, recommendation detail, milestone toggle, and contact.
- `modified:   recommender/views.py`: Streamlined views delegating to `services/`, added rate limiting and pure Python `smtplib` mailer.
- `modified:   recommender/tests.py`: Comprehensive test suite testing static finders, schemas, scoring, link builders, and mocked LLM flows.
- `modified:   skill_recommender/settings.py`: Added `GROQ_MODEL`, `YOUTUBE_API_KEY`, `GITHUB_TOKEN`, configured WhiteNoise.

#### Templates
- `modified:   templates/recommender/base.html`: Minimal semantic layout with system font stack, SVG brand logo, tiny text nav, and single-line footer.
- `modified:   templates/recommender/home.html`: Clean landing page with active roadmap resume link and CTA.
- `modified:   templates/recommender/login.html`: Auth form with centered 48px logo and semantic inputs.
- `modified:   templates/recommender/register.html`: Registration form with centered 48px logo and password confirmation.
- `modified:   templates/recommender/logout.html`: Minimal logged-out confirmation page.
- `modified:   templates/recommender/profile.html`: Preference form, assessment history, level progression, and re-assess actions.
- `modified:   templates/recommender/skill_assessment.html`: Adaptive wizard: free-text skill input -> 1-question per screen card flow -> submit.
- `modified:   templates/recommender/recommendation_detail.html`: Detailed printable roadmap, interactive progress checklist, and curated links.
- `modified:   templates/recommender/recommendations.html`: Index of generated roadmaps.
- `modified:   templates/recommender/about.html`: Platform mission and 3-step workflow.
- `modified:   templates/recommender/contact.html`: Minimal contact form with category selector.
- `modified:   templates/recommender/resources.html`: Curated documentation and women-in-tech communities index.

### Verification: Zero Node/Bootstrap/jQuery/CDN Artifacts

Command run:
```bash
find . -name "package.json" -o -name "node_modules"
```
Output:
```text
./venv/lib/python3.14/site-packages/playwright/driver/package/package.json
```
*(No `package.json` or `node_modules` exists in the project root or source tree).*

Command run:
```bash
grep -rnE "(bootstrap|jquery|cdn\.jsdelivr|cdnjs\.cloudflare|fonts\.googleapis)" templates/ static/ recommender/*.py skill_recommender/*.py
```
Output:
```text
(0 matches found - command exited with status 1)
```

Command run:
```bash
grep -rnE "(<link rel=\"stylesheet\"|<script src=)" templates/
```
Output:
```text
templates/recommender/base.html:21:  <link rel="stylesheet" href="{% static 'css/app.css' %}">
templates/recommender/base.html:77:  <script src="{% static 'js/app.js' %}"></script>
```

---

## 3. UI AND BRANDING

### Redesigned Pages
All 12 templates were stripped and rebuilt using the minimal monochrome design system:
1. `home.html` (Landing & CTA)
2. `login.html` (Authentication)
3. `register.html` (Account registration)
4. `logout.html` (Session termination)
5. `profile.html` (Learner profile & assessment history)
6. `skill_assessment.html` (Adaptive assessment wizard)
7. `recommendation_detail.html` (Printable roadmap & checklist)
8. `recommendations.html` (Roadmap index)
9. `resources.html` (Curated link directory)
10. `about.html` (Mission & overview)
11. `contact.html` (Inquiry form)
12. `base.html` (Global layout & navigation)

### Asset Sizes
- `static/css/app.css`: **8,812 bytes** (~8.6 KB uncompressed).
- `static/js/app.js`: **4,407 bytes** (~4.3 KB uncompressed).
- `static/img/skillher-icon.svg`: **1,804 bytes**.
- `static/img/skillher-logo.svg`: **2,122 bytes**.

### Logo & Favicon Integration
- **Favicon**: Embedded in `<head>` of [base.html](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/templates/recommender/base.html#L18) via `<link rel="icon" href="{% static 'img/skillher-icon.svg' %}" type="image/svg+xml">`.
- **Top Navigation Logo**: Placed in site header via `<a href="{% url 'home' %}" class="brand"><img src="{% static 'img/skillher-logo.svg' %}" alt="SkillHer" height="32"></a>`.
- **Auth Pages**: Displayed centered at 48px height above login and register forms (`<img src="{% static 'img/skillher-logo.svg' %}" alt="SkillHer" height="48">`).
- **Printable Header**: Dedicated print header rendered at top of page in black via `@media print`.

### Dark Mode Verification
Automatic dark mode is natively implemented without JavaScript dependencies:
- In `static/css/app.css`, `@media (prefers-color-scheme: dark)` overrides:
  - `--bg`: `#111111`
  - `--fg`: `#f5f5f5`
  - `--muted`: `#a3a3a3`
  - `--accent`: `#f472b6` (matches dark SVG branding)
  - `--border`: `#2a2a2a`
  - `--input-bg`: `#181818`
- In both SVG files (`skillher-icon.svg` and `skillher-logo.svg`), embedded `<style>` blocks contain `@media (prefers-color-scheme: dark)` shifting `--fg-color` from `#111111` to `#f5f5f5` and `--accent-color` from `#b83280` to `#f472b6`.
- In [base.html](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/templates/recommender/base.html#L14-L15), `<meta name="theme-color">` is defined for both light (`#ffffff`) and dark (`#111111`) modes.

---

## 4. SKILL ASSESSMENT ENGINE

### Workflow
1. **Input**: User inputs skill name (free text), primary career goal (select), and weekly available hours (integer).
2. **Generation**: `generate_skill_questions(skill_name, goal)` queries Groq LLM using a structured prompt requesting strict JSON. It produces:
   - 4 Concept-check MCQs (options A–D, 1 correct answer).
   - 2 Practical scenario MCQs (real-world challenge, 1 correct answer).
   - 2 Self-rating questions (1–5 scale, evaluating hands-on depth and unblocking confidence).
3. **Validation**: `validate_question_schema(data)` checks that output contains at least 6 valid question dictionaries with non-empty texts, topics, options, and valid `correct_option` keys ('a'–'d').
4. **Offline Fallback**: If Groq returns non-JSON, errors, or fails validation, `build_generic_fallback_questions(skill_name)` (or a curated Python bank) immediately provides an 8-question evaluation without crashing.
5. **Server-Side Scoring**:
   - `score_assessment(questions_with_answers)` executes entirely on the server.
   - Objective questions carry weight 2.0; user option is matched against `correct_option`.
   - Self-ratings carry weight 1.0; 1–5 scale is mapped from 20% to 100%.
   - Overall score percentage is calculated: `< 45%` = `Beginner`, `45%–75%` = `Intermediate`, `> 75%` = `Advanced`.
   - Per-topic scores are calculated to separate `strengths` (&ge; 65%) from `gaps` (< 65%).
6. **UI Rendering**: Questions are presented 1 question per screen with card steps, minimal progress counter (`"3 / 8"`), and no artificial timers. Falls back to a stacked form if JavaScript is disabled.

### Models & Migrations
- `Assessment`: User profile, skill name, goal, weekly hours, level, score percentage, strengths (JSONField), gaps (JSONField), summary, completed.
- `AssessmentQuestion`: Foreign key to `Assessment`, question type (`mcq`, `scenario`, `rating`), topic, options A–D, correct option, difficulty, order.
- `AssessmentAnswer`: Foreign key to `Assessment` and `AssessmentQuestion`, selected option, rating value, is_correct boolean.
- Applied in migration `0004_alter_assessmentquestion_options_and_more.py`.

---

## 5. RECOMMENDATION ENGINE

### Content of a Recommendation
Each generated recommendation includes:
1. **Gap Summary**: 3–5 lines synthesizing current readiness and immediate priorities.
2. **Weekly Roadmap**: 4-week sprint (&le; 8 hrs/week) or 12-week comprehensive path with weekly milestone outcomes and checklist items.
3. **Weekly YouTube Tutorials**: Video search links matching that specific week's topic.
4. **Portfolio Projects**: 2–3 projects tailored to learner level with recruiter highlight notes.
5. **Curated Resources**:
   - *GitHub*: Top-starred repos, awesome lists, and starter kits.
   - *Internships*: Dedicated search queries on LinkedIn, Internshala, Indeed, and Google Jobs.
   - *Courses & Official Docs*: Direct official docs mapping (Python, React, Django, SQL, etc.) + freeCodeCamp, Coursera, edX, Khan Academy.
   - *Communities*: Women Who Code, AnitaB.org/Grace Hopper Celebration, Rewriting the Code, Ada's List.
   - *Certifications*: Recognized free and verified certificates.
6. **Career Advice**: Resume bullet tips and core technical interview prep topics.

### Link Integrity & Deterministic Builders
**The LLM is strictly forbidden from outputting raw URLs.** The system prompt enforces:
> "CRITICAL: DO NOT OUTPUT ANY URLs OR LINKS! The backend server constructs deterministic links. Only output keywords, titles, descriptions, and topics."

All links are built deterministically in [recommender/services/links.py](file:///Users/malthumkarvarun/LLM%20working/skill_recommender/recommender/services/links.py) using `urllib.parse.quote_plus`:
- **YouTube**: Default URL: `https://www.youtube.com/results?search_query=<kw>`.
- **GitHub**: Default URL: `https://github.com/search?q=<kw>&type=repositories`.
- **LinkedIn Jobs**: `https://www.linkedin.com/jobs/search/?keywords=<skill>+intern&location=<loc>`.
- **Internshala**: `https://internshala.com/internships/keywords-<skill>`.
- **Indeed**: `https://www.indeed.com/jobs?q=<skill>+intern&l=<loc>`.
- **Google Jobs**: `https://www.google.com/search?q=<skill>+intern+jobs+<loc>&ibp=htl;jobs`.
- **freeCodeCamp**: `https://www.freecodecamp.org/news/search/?query=<kw>`.
- **Coursera**: `https://www.coursera.org/search?query=<kw>`.
- **Official Docs**: Exact lookup against `OFFICIAL_DOCS_MAP` mapping known skills to official documentation (`docs.python.org`, `react.dev`, `docs.djangoproject.com`, `postgresql.org`, `docs.docker.com`, etc.).

### Caching & API Quota Handling
- YouTube Data API v3 and GitHub REST API calls are wrapped in `try/except` with a 5-second timeout.
- Successful API results are cached in Django's cache (`cache.set`) for 24 hours (86,400 seconds).
- **Graceful Degradation**: If YouTube quota is exceeded (HTTP 403), rate-limited, or keys are absent, the helper silently catches the error and falls back to verified YouTube search query URLs. No errors or warnings are shown to the end user.

---

## 6. ENVIRONMENT VARIABLES

### Variable Inventory

| Variable Name | Required | Status in Code | Status in `.env.example` | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `SECRET_KEY` | **Required** | Read in `settings.py` | Present | Django secret cryptographic key |
| `DEBUG` | Optional | Read in `settings.py` | Present | Debug toggle (`True` / `False`) |
| `GROQ_API_KEY` | **Required** | Read in `settings.py`, `llm.py` | Present | Groq Cloud API authentication key |
| `GROQ_MODEL` | Optional | Read in `settings.py`, `llm.py` | Present | Groq model (`llama-3.3-70b-versatile`) |
| `YOUTUBE_API_KEY` | Optional | Read in `settings.py`, `links.py` | Present | YouTube Data API v3 key |
| `GITHUB_TOKEN` | Optional | Read in `settings.py`, `links.py` | Present | GitHub personal access token |
| `DATABASE_URL` | Optional | Read in `settings.py` | Present | Managed PostgreSQL connection string |
| `CONTACT_EMAIL` | Optional | Read in `views.py` | Present | Recipient email for contact forms |
| `SMTP_HOST` | Optional | Read in `views.py` | Present | SMTP server hostname |
| `SMTP_PORT` | Optional | Read in `views.py` | Present | SMTP port (e.g. 587) |
| `SMTP_USER` | Optional | Read in `views.py` | Present | SMTP authentication username |
| `SMTP_PASS` | Optional | Read in `views.py` | Present | SMTP app password |
| `DB_NAME` | Optional | Read in `settings.py` | Missing from `.env.example` | Standalone DB name parameter |
| `DB_ENGINE` | Optional | Read in `settings.py` | Missing from `.env.example` | Standalone DB engine parameter |
| `DB_USER` | Optional | Read in `settings.py` | Missing from `.env.example` | Standalone DB user parameter |
| `DB_PASSWORD` | Optional | Read in `settings.py` | Missing from `.env.example` | Standalone DB password parameter |
| `DB_HOST` | Optional | Read in `settings.py` | Missing from `.env.example` | Standalone DB host parameter |
| `DB_PORT` | Optional | Read in `settings.py` | Missing from `.env.example` | Standalone DB port parameter |
| `VERCEL` | Optional | Read in `settings.py` | Omitted by design | Automated Vercel runtime flag |
| `AWS_LAMBDA_FUNCTION_NAME` | Optional | Read in `settings.py` | Omitted by design | Serverless runtime flag |
| `LAMBDA_TASK_ROOT` | Optional | Read in `settings.py` | Omitted by design | Serverless runtime flag |

---

## 7. TESTING

### Command Execution & Results

#### 1. System Check
```bash
DATABASE_URL="" ./venv/bin/python manage.py check
```
Output:
```text
System check identified no issues (0 silenced).
```
**Status: PASS**

#### 2. Migration Status
```bash
DATABASE_URL="" ./venv/bin/python manage.py showmigrations
```
Output:
```text
admin [X] 0001_initial ... [X] 0003_logentry_add_action_flag_choices
auth [X] 0001_initial ... [X] 0012_alter_user_first_name_max_length
contenttypes [X] 0001_initial ... [X] 0002_remove_content_type_name
recommender [X] 0001_initial ... [X] 0004_alter_assessmentquestion_options_and_more
sessions [X] 0001_initial
```
**Status: ALL APPLIED (100%)**

#### 3. Automated Test Suite
```bash
DATABASE_URL="" ./venv/bin/python manage.py test -v 2
```
Output:
```text
Found 11 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, recommender, sessions
...
test_happy_path_assessment_to_roadmap (recommender.tests.AssessmentAndRoadmapViewsTestCase) ... ok
test_milestone_toggle_api (recommender.tests.AssessmentAndRoadmapViewsTestCase) ... ok
test_contact_form_saves_to_database (recommender.tests.ContactAndPublicPagesTestCase) ... ok
test_public_pages_load (recommender.tests.ContactAndPublicPagesTestCase) ... ok
test_assessment_schema_validation_and_fallback (recommender.tests.ServiceLogicTestCase) ... ok
test_link_builders_url_encoding_and_integrity (recommender.tests.ServiceLogicTestCase) ... ok
test_roadmap_schema_validation (recommender.tests.ServiceLogicTestCase) ... ok
test_scoring_engine_objective_and_rating (recommender.tests.ServiceLogicTestCase) ... ok
test_base_template_renders_branding (recommender.tests.TemplateAndStaticAssetsTestCase) ... ok
test_login_and_register_pages_render_48px_logo (recommender.tests.TemplateAndStaticAssetsTestCase) ... ok
test_static_logo_and_icon_exist_on_filesystem (recommender.tests.TemplateAndStaticAssetsTestCase) ... ok

----------------------------------------------------------------------
Ran 11 tests in 3.681s

OK
Destroying test database for alias 'default'...
```
**Status: 11 PASSED, 0 FAILED, 0 ERRORS**

### Verification Scope

#### Verified:
- All public route HTTP 200 responses (`/`, `/login/`, `/register/`, `/about/`, `/contact/`).
- Authenticated route accessibility (`/profile/`, `/assess/`, `/resources/`, `/recommendations/`).
- Assessment schema validation logic and curated question fallback generation.
- Server-side scoring calculation (both weighted MCQs and 1–5 self-ratings).
- Deterministic URL builders with URL-encoding for YouTube, GitHub, LinkedIn, Internshala, and documentation.
- Happy-path integration flow from skill submission to assessment completion to roadmap rendering.
- Milestone toggle API persisting checklist updates to the database.
- Static file resolution via `finders.find` for `css/app.css`, `js/app.js`, `img/skillher-logo.svg`, and `img/skillher-icon.svg`.
- `collectstatic` copying assets to `staticfiles/` for WhiteNoise compression.

#### NOT Verified / Untested:
- **Human Visual Rendering**: Visual verification in an active browser rendering window was not manually conducted.
- **Live Groq API Execution**: Live network calls to Groq API with active credentials were not executed during tests (mocked to prevent API costs and network flakes; offline fallbacks tested).
- **Live Real-World Email Delivery**: While `test_contact_form_saves_to_database` verified database persistence and error handling, an actual live email dispatch through Gmail SMTP servers was not initiated.
- **Production Vercel Cloud Runtime**: Actual live deployment execution on Vercel's edge network was not run.

---

## 8. DEPLOYMENT

### Vercel Considerations
1. **Static File Serving**:
   - Django settings use `whitenoise.middleware.WhiteNoiseMiddleware` with `CompressedStaticFilesStorage`.
   - Vercel routes all requests to `skill_recommender/wsgi.py`. WhiteNoise handles static assets directly from `staticfiles/`.
2. **Ephemeral Filesystem Limitation**:
   - Vercel Lambdas are ephemeral and read-only outside `/tmp/`.
   - `settings.py` automatically falls back to `/tmp/db.sqlite3` in serverless environments (`VERCEL` env var detected).
   - *Requirement for Persistence*: A managed PostgreSQL database URL (e.g. Neon, Supabase, AWS RDS) must be supplied via `DATABASE_URL` so users, assessments, and roadmaps persist across function cold starts.
3. **Environment Variables**:
   - `GROQ_API_KEY`: Groq inference key.
   - `GROQ_MODEL`: `llama-3.3-70b-versatile`.
   - `SECRET_KEY`: Production secret key.
   - `DATABASE_URL`: Hosted PostgreSQL connection string.

### Exact Deployment Steps
1. **Commit and Push**:
   ```bash
   git add .
   git commit -m "feat: complete redesign and rebrand as SkillHer"
   git push origin main
   ```
2. **Import Project into Vercel**:
   - Select repository `varun05126/llm_working`.
   - In **Project Settings**, set **Root Directory** to `skill_recommender`.
   - Ensure Framework Preset is **Other** (`vercel.json` dictates `@vercel/python`).
3. **Configure Environment Variables in Vercel Dashboard**:
   - In **Settings > Environment Variables**, add:
     - `GROQ_API_KEY`
     - `GROQ_MODEL`
     - `SECRET_KEY`
     - `DATABASE_URL`
4. **Deploy**:
   - Click **Deploy**. Vercel will install `requirements.txt`, run `collectstatic`, and serve the app.

---

## 9. KNOWN ISSUES AND RISKS

1. **Active Secret Strings in Repository Files**:
   - While `.env` is properly ignored in `.gitignore`, existing `.env.local` or historical files on earlier commits may contain actual or expired keys. Developers should rotate all Groq and SMTP credentials before making the repository public.
2. **Serverless SQLite Ephemerality**:
   - If `DATABASE_URL` is omitted on Vercel, the app falls back to `/tmp/db.sqlite3`. Any user registrations or generated roadmaps will reset when the serverless container recycles.
3. **External API Rate Limits & Quotas**:
   - Free-tier Groq API keys have RPM/TPM limits. If rate limits are exceeded, the app smoothly falls back to curated offline banks and plans, but real-time LLM personalization will pause until the quota window resets.
   - GitHub API requests without a `GITHUB_TOKEN` have an unauthenticated IP rate limit of 60 requests/hour.
4. **Input Sanitization vs Complex Skill Names**:
   - `sanitize_input()` strips non-printable characters and limits string lengths to 1,500 characters. Skills with special characters (e.g., `C++` or `C#`) are properly preserved and URL-encoded, but skills exceeding 100 characters are truncated.

---

## 10. NEXT STEPS (Top 5 Recommended Improvements)

1. **Persistent PostgreSQL Connection on Vercel**:
   - Provision a free managed Neon PostgreSQL database and connect via `DATABASE_URL` in Vercel settings to eliminate ephemeral SQLite data resets.
2. **Live Visual Smoke Test**:
   - Launch dev server locally (`python manage.py runserver`) and inspect all pages in a browser to review typography hierarchy, dark mode toggling, and mobile viewport responsiveness.
3. **Question Set Database Caching**:
   - Cache generated question sets in the database by normalized skill name (e.g., store a reusable pool of 20 questions for "Data Analysis") so subsequent users requesting the same skill do not incur repetitive Groq API calls.
4. **Credential Rotation & Secret Scrubbing**:
   - Rotate all Groq API keys and Google App Passwords, and run `git-filter-repo` or BFG Repo-Cleaner if any credentials were ever committed to past git commits.
5. **Interactive Skill Badge Export**:
   - Add an inline SVG certificate or achievement badge generator on the assessment results page allowing learners to export or share their verified assessed tier (`Beginner`, `Intermediate`, `Advanced`) on LinkedIn.
