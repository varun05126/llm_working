import logging
from .llm import query_groq
from .links import (
    build_youtube_links,
    build_github_links,
    build_internship_links,
    build_course_and_doc_links,
    build_community_and_cert_links
)

logger = logging.getLogger(__name__)


def generate_curated_fallback_roadmap(skill: str, level: str, weekly_hours: int, goal: str) -> dict:
    """Deterministic fallback roadmap when Groq API is unavailable."""
    is_short = weekly_hours <= 8 or level == 'Advanced'
    num_weeks = 4 if is_short else 12

    gap_summary = (
        f"Based on your assessment in {skill} ({level} tier), your core foundations are established, "
        f"but bridging into professional production readiness requires deliberate hands-on practice. "
        f"With {weekly_hours} hours available weekly, this roadmap focuses on eliminating gaps in real-world "
        f"tooling, robust debugging, and portfolio-grade project deliverables."
    )

    weeks = []
    if num_weeks == 4:
        milestones = [
            ("Core Deep-Dive & Conventions", "Idiomatic syntax, best practices, and standard patterns"),
            ("Application Architecture", "Modular design, error boundaries, and state management"),
            ("Real-World Integration & APIs", "Connecting services, handling async flows, and automated testing"),
            ("Production Delivery & Showcase", "Packaging, deployment, documentation, and portfolio polish")
        ]
    else:
        milestones = [
            ("Month 1: Foundations", "Syntax, data models, version control, and development environments"),
            ("Month 1: Problem Solving", "Algorithmic thinking, data transformation, and clean code"),
            ("Month 1: Core Testing", "Unit test suites, mocking, and edge-case handling"),
            ("Month 1: Milestone Review", "Independent mini-project integrating weeks 1-3"),
            ("Month 2: Application Layer", "Component architecture, API contracts, and async programming"),
            ("Month 2: Performance & Profiling", "Memory management, query optimization, and latency reduction"),
            ("Month 2: Tooling & Toolchains", "Modern build tools, linters, formatters, and dependency audits"),
            ("Month 2: Milestone Review", "Full-featured application with database persistence"),
            ("Month 3: System Design", "Scalability trade-offs, caching layers, and security best practices"),
            ("Month 3: Cloud & Deployment", "Containerization with Docker, CI/CD pipelines, and cloud hosting"),
            ("Month 3: Observability", "Structured logging, metrics tracking, and error monitoring"),
            ("Month 3: Final Portfolio Capstone", "Production-grade project with live demo and technical documentation")
        ]

    for idx, (title, outcome) in enumerate(milestones, start=1):
        topic_kw = f"{skill} {title.split(':')[-1].strip()}"
        weeks.append({
            'week_number': idx,
            'title': f"Week {idx}: {title}",
            'topic': topic_kw,
            'concrete_outcome': outcome,
            'items': [
                f"Study key concepts for {title.lower()}",
                f"Complete hands-on coding exercises ({weekly_hours} hrs dedicated)",
                f"Document key learnings and push progress to GitHub"
            ]
        })

    projects = [
        {
            'title': f"{skill} Practical Dashboard & Service",
            'difficulty': level,
            'description': f"Build a clean, production-oriented application utilizing {skill} with external API integration, data persistence, and input validation.",
            'portfolio_highlight': "Demonstrates clean architecture, error resiliency, and modern engineering standards."
        },
        {
            'title': f"{skill} Open Source Tool / Package",
            'difficulty': 'Intermediate',
            'description': f"Develop an open-source utility, library, or starter kit that solves a recurring challenge for other developers working in {skill}.",
            'portfolio_highlight': "Proves ability to write modular, reusable code with comprehensive documentation and tests."
        }
    ]

    resume_tips = [
        f"Highlight specific quantifiable achievements with {skill} (e.g. 'Improved data retrieval time by 35%').",
        "Include links to clean GitHub repositories with thorough READMEs, architecture diagrams, and test suites.",
        "Emphasize testing frameworks and CI/CD pipelines used in your portfolio projects."
    ]

    interview_topics = [
        f"Core principles, memory model, and idioms of {skill}",
        "Trade-offs between different architectural approaches and libraries",
        "Debugging complex bugs and analyzing production error logs"
    ]

    return {
        'gap_summary': gap_summary,
        'roadmap': weeks,
        'projects': projects,
        'resume_tips': resume_tips,
        'interview_topics': interview_topics
    }


def validate_roadmap_schema(data: dict) -> bool:
    """Validate that LLM output matches the structured roadmap schema."""
    if not isinstance(data, dict):
        return False
    if not data.get('gap_summary') or not isinstance(data.get('roadmap'), list):
        return False
    if len(data.get('roadmap')) < 3:
        return False
    for week in data['roadmap']:
        if not isinstance(week, dict) or not week.get('title') or not week.get('concrete_outcome'):
            return False
    return True


def generate_recommendation_plan(skill: str, level: str, weekly_hours: int, goal: str, location: str = "") -> dict:
    """
    Generate personalized learning path combining Groq LLM (for synthesis and curriculum)
    with strict backend deterministic link builders (YouTube, GitHub, Internships, Docs, Communities).
    NEVER allows the LLM to output raw URLs.
    """
    is_short = weekly_hours <= 8 or level == 'Advanced'
    target_weeks = 4 if is_short else 12

    system_prompt = (
        "You are an expert curriculum designer and career mentor for SkillHer. "
        "Create an actionable, realistic learning roadmap. "
        "CRITICAL: DO NOT OUTPUT ANY URLs OR LINKS! The backend server constructs deterministic links. "
        "Only output keywords, titles, descriptions, and topics. "
        "Output ONLY valid JSON matching the exact schema."
    )

    user_prompt = f"""Design a {target_weeks}-week personalized roadmap for:
Skill: "{skill}"
Assessed Level: {level}
Weekly Hours: {weekly_hours}
Career Goal: {goal}

JSON Schema:
{{
  "gap_summary": "3-5 lines explaining exact gaps identified at the {level} tier and how to bridge them.",
  "roadmap": [
    {{
      "week_number": 1,
      "title": "Week 1: Foundations & Architecture",
      "topic": "Keyword search topic for tutorials",
      "concrete_outcome": "Deliverable built this week",
      "items": [
        "Milestone checklist item 1",
        "Milestone checklist item 2"
      ]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "difficulty": "{level}",
      "description": "Project overview",
      "portfolio_highlight": "Why recruiters will love this"
    }}
  ],
  "resume_tips": [
    "Concrete tip for showcasing {skill} on a resume",
    "Concrete portfolio tip"
  ],
  "interview_topics": [
    "Interview technical topic 1",
    "Interview technical topic 2"
  ]
}}
"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    llm_output = query_groq(messages, response_format_json=True, temperature=0.3, retries=1)

    if not llm_output or not validate_roadmap_schema(llm_output):
        logger.warning(f"Groq roadmap generation unavailable or schema invalid for '{skill}'. Using curated fallback.")
        plan_data = generate_curated_fallback_roadmap(skill, level, weekly_hours, goal)
    else:
        logger.info(f"Successfully generated structured roadmap for '{skill}' via Groq.")
        plan_data = llm_output

    # Enrich each weekly topic with deterministic YouTube links
    for week in plan_data.get('roadmap', []):
        topic_term = week.get('topic') or f"{skill} {week.get('title', '')}"
        week['youtube_links'] = build_youtube_links(topic_term)

    # Enrich with deterministic resources (No LLM URL hallucinations)
    resources_data = {
        'github_repos': build_github_links(skill),
        'internships': build_internship_links(skill, location),
        'courses_and_docs': build_course_and_doc_links(skill),
        'community_and_certs': build_community_and_cert_links(skill)
    }

    plan_data['resources_data'] = resources_data
    return plan_data
