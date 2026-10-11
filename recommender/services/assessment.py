import logging
from .llm import query_groq

logger = logging.getLogger(__name__)

# Curated Fallback Question Banks for Offline / Degraded Mode
CURATED_FALLBACK_BANK = {
    'python': [
        {
            'order': 1,
            'question_type': 'mcq',
            'topic': 'Data Structures',
            'difficulty': 'beginner',
            'question_text': 'Which Python built-in data type is mutable and maintains insertion order?',
            'option_a': 'tuple',
            'option_b': 'list',
            'option_c': 'frozenset',
            'option_d': 'str',
            'correct_option': 'b',
            'explanation': 'Lists in Python are mutable ordered sequences.'
        },
        {
            'order': 2,
            'question_type': 'mcq',
            'topic': 'Control Flow',
            'difficulty': 'beginner',
            'question_text': 'What is the primary purpose of the "with" statement when handling files in Python?',
            'option_a': 'It accelerates disk write speeds.',
            'option_b': 'It automatically manages resource cleanup and ensures file closure.',
            'option_c': 'It encrypts file content during reads.',
            'option_d': 'It parses JSON contents automatically.',
            'correct_option': 'b',
            'explanation': 'The with statement acts as a context manager guaranteeing resources are closed.'
        },
        {
            'order': 3,
            'question_type': 'scenario',
            'topic': 'Object-Oriented Programming',
            'difficulty': 'intermediate',
            'question_text': 'You need to prevent callers from modifying an attribute directly while calculating its value on-demand. What Python feature should you use?',
            'option_a': '@staticmethod decorator',
            'option_b': '__slots__ allocation',
            'option_c': '@property decorator with a getter',
            'option_d': 'Global module variables',
            'correct_option': 'c',
            'explanation': '@property exposes a getter method as an attribute, allowing controlled computed access.'
        },
        {
            'order': 4,
            'question_type': 'mcq',
            'topic': 'Generators & Memory',
            'difficulty': 'intermediate',
            'question_text': 'Why would a developer choose a generator expression over a list comprehension for a 10-million line log file?',
            'option_a': 'Generators run concurrently across all CPU cores.',
            'option_b': 'Generators stream items lazily with constant memory O(1).',
            'option_c': 'List comprehensions cannot process string data.',
            'option_d': 'Generators automatically cache results on disk.',
            'correct_option': 'b',
            'explanation': 'Generators yield one item at a time, avoiding storing the entire dataset in RAM.'
        },
        {
            'order': 5,
            'question_type': 'scenario',
            'topic': 'Concurrency & Async',
            'difficulty': 'advanced',
            'question_text': 'Your service spends 95% of its execution time waiting for HTTP responses from third-party APIs. Which concurrency model is most appropriate?',
            'option_a': 'CPU multiprocessing pool',
            'option_b': 'Single-threaded synchronous blocking loops',
            'option_c': 'Asynchronous I/O with asyncio or thread pooling',
            'option_d': 'C-extension recompilation',
            'correct_option': 'c',
            'explanation': 'I/O-bound tasks benefit drastically from cooperative async loops or thread pools.'
        },
        {
            'order': 6,
            'question_type': 'mcq',
            'topic': 'Error Handling',
            'difficulty': 'intermediate',
            'question_text': 'What happens if a code block raises an uncaught exception inside a "try" block followed by a "finally" block?',
            'option_a': 'The "finally" block is skipped to prevent crashing.',
            'option_b': 'The "finally" block executes first, and then the exception propagates.',
            'option_c': 'The exception is silently swallowed.',
            'option_d': 'The program immediately terminates without running any remaining code.',
            'correct_option': 'b',
            'explanation': 'Finally blocks always execute regardless of whether an exception was handled.'
        },
        {
            'order': 7,
            'question_type': 'rating',
            'topic': 'Practical Debugging',
            'difficulty': 'self-assessment',
            'question_text': 'How comfortable are you reading stack traces, using pdb/breakpoints, and diagnosing performance bottlenecks?',
            'option_a': '1 - Need guidance',
            'option_b': '2 - Basic prints',
            'option_c': '3 - Comfortable with debugger',
            'option_d': '4 - Proficient profiling',
            'correct_option': '',
            'explanation': 'Self-rating (1 to 5 scale)'
        },
        {
            'order': 8,
            'question_type': 'rating',
            'topic': 'Packaging & Standards',
            'difficulty': 'self-assessment',
            'question_text': 'Rate your familiarity with Python packaging (pyproject.toml, virtual environments, pip) and PEP 8 style standards.',
            'option_a': '1 - Unfamiliar',
            'option_b': '2 - Basic venv',
            'option_c': '3 - Moderate familiarity',
            'option_d': '4 - Confident with tooling',
            'correct_option': '',
            'explanation': 'Self-rating (1 to 5 scale)'
        }
    ]
}


def build_generic_fallback_questions(skill_name: str) -> list:
    """Generate a high-quality fallback question set for any skill when LLM is unavailable."""
    return [
        {
            'order': 1,
            'question_type': 'mcq',
            'topic': 'Core Principles',
            'difficulty': 'beginner',
            'question_text': f'What is the foundational starting concept when approaching {skill_name} in professional projects?',
            'option_a': 'Mastering core syntax, conventions, and mental models before complex tooling.',
            'option_b': 'Copying production architectures without understanding fundamentals.',
            'option_c': 'Avoiding version control and automated testing.',
            'option_d': 'Focusing exclusively on edge-case micro-optimizations.',
            'correct_option': 'a',
            'explanation': 'Solid foundational knowledge and idioms are essential before moving to advanced abstractions.'
        },
        {
            'order': 2,
            'question_type': 'mcq',
            'topic': 'Tooling & Environment',
            'difficulty': 'beginner',
            'question_text': f'In standard modern workflows for {skill_name}, why is environment reproducibility crucial?',
            'option_a': 'It restricts software from ever changing.',
            'option_b': 'It ensures consistent behavior across developer machines and production environments.',
            'option_c': 'It completely eliminates the need for software licenses.',
            'option_d': 'It replaces the need for code review.',
            'correct_option': 'b',
            'explanation': 'Reproducibility prevents "works on my machine" defects.'
        },
        {
            'order': 3,
            'question_type': 'scenario',
            'topic': 'Problem Solving',
            'difficulty': 'intermediate',
            'question_text': f'When designing a production solution in {skill_name}, you encounter unexpected behavior. What is the recommended troubleshooting flow?',
            'option_a': 'Rewrite the entire codebase from scratch.',
            'option_b': 'Isolate inputs with a minimal reproducible example, inspect logs, and test hypotheses.',
            'option_c': 'Deploy immediately to production to see if user traffic fixes it.',
            'option_d': 'Ignore the issue if tests pass on one local machine.',
            'correct_option': 'b',
            'explanation': 'Systematic isolation and verification leads to reliable debugging.'
        },
        {
            'order': 4,
            'question_type': 'mcq',
            'topic': 'Quality & Testing',
            'difficulty': 'intermediate',
            'question_text': f'How does automated testing and validation support long-term mastery of {skill_name}?',
            'option_a': 'It prevents other team members from contributing.',
            'option_b': 'It builds confidence during refactoring and establishes executable contracts.',
            'option_c': 'It makes code run 10x faster automatically.',
            'option_d': 'It replaces software architecture design.',
            'correct_option': 'b',
            'explanation': 'Automated tests catch regressions and document expected system behavior.'
        },
        {
            'order': 5,
            'question_type': 'scenario',
            'topic': 'Architecture & Scale',
            'difficulty': 'advanced',
            'question_text': f'As your work in {skill_name} scales to larger systems and teams, which principle ensures maintainability?',
            'option_a': 'Monolithic single-file implementations with tight coupling.',
            'option_b': 'Modular separation of concerns with clear interfaces and documentation.',
            'option_c': 'Using no comments, tests, or documentation.',
            'option_d': 'Hardcoding environment credentials in repository code.',
            'correct_option': 'b',
            'explanation': 'Separation of concerns allows teams to safely iterate and scale.'
        },
        {
            'order': 6,
            'question_type': 'mcq',
            'topic': 'Security & Best Practices',
            'difficulty': 'intermediate',
            'question_text': f'Which practice is universally critical when applying {skill_name} in production systems?',
            'option_a': 'Validating and sanitizing all external inputs and securely managing secrets.',
            'option_b': 'Storing credentials in plain text in public repositories.',
            'option_c': 'Disabling error handling to suppress crash warnings.',
            'option_d': 'Running all processes with root / unrestricted administrative privileges.',
            'correct_option': 'a',
            'explanation': 'Defense in depth and input validation are universal engineering requisites.'
        },
        {
            'order': 7,
            'question_type': 'rating',
            'topic': 'Hands-On Experience',
            'difficulty': 'self-assessment',
            'question_text': f'Rate your hands-on experience building independent, end-to-end projects with {skill_name}.',
            'option_a': '1 - Just starting out',
            'option_b': '2 - Followed tutorials',
            'option_c': '3 - Built 1-2 small projects',
            'option_d': '4 - Confident building from scratch',
            'correct_option': '',
            'explanation': 'Self-rating (1 to 5 scale)'
        },
        {
            'order': 8,
            'question_type': 'rating',
            'topic': 'Confidence & Troubleshooting',
            'difficulty': 'self-assessment',
            'question_text': f'How confident are you independently unblocking yourself when encountering errors in {skill_name}?',
            'option_a': '1 - Frequently stuck',
            'option_b': '2 - Rely heavily on search',
            'option_c': '3 - Able to diagnose most issues',
            'option_d': '4 - Highly self-sufficient',
            'correct_option': '',
            'explanation': 'Self-rating (1 to 5 scale)'
        }
    ]


def validate_question_schema(data: dict) -> bool:
    """Validate that the LLM returned questions conforming to the structured schema."""
    if not isinstance(data, dict):
        return False
    questions = data.get('questions')
    if not isinstance(questions, list) or len(questions) < 6:
        return False

    for q in questions:
        if not isinstance(q, dict):
            return False
        if not q.get('question_text') or not q.get('topic'):
            return False
        q_type = q.get('question_type', 'mcq')
        if q_type in ('mcq', 'scenario'):
            if not q.get('option_a') or not q.get('option_b'):
                return False
            if q.get('correct_option', '').lower() not in ('a', 'b', 'c', 'd'):
                return False
    return True


def generate_skill_questions(skill_name: str, goal: str = "Career Advancement") -> list:
    """
    Generate 8-10 adaptive questions specific to skill_name using Groq LLM.
    Strict JSON output, schema validation, fallback on error.
    """
    cleaned_skill = skill_name.strip()
    key = cleaned_skill.lower()
    if key in CURATED_FALLBACK_BANK:
        # Check if fast curated bank exists
        pass

    system_prompt = (
        "You are an expert technical interviewer and educator for SkillHer. "
        "Your role is to assess learners fairly, accurately, and without bias. "
        "Output ONLY valid JSON matching the exact schema requested. Do not include markdown preamble or conversational text."
    )

    user_prompt = f"""Generate an 8-question adaptive skill assessment specifically for: "{cleaned_skill}".
Learner Goal: {goal}.

Include:
- 4 Concept-check multiple choice questions (orders 1-4, progression from beginner to intermediate, with one correct option: 'a', 'b', 'c', or 'd').
- 2 Practical scenario questions (orders 5-6, intermediate to advanced real-world challenges, with one correct option: 'a', 'b', 'c', or 'd').
- 2 Self-rating questions (orders 7-8, 'rating' type, evaluating confidence and hands-on depth, correct_option must be empty "").

JSON Schema:
{{
  "skill": "{cleaned_skill}",
  "questions": [
    {{
      "order": 1,
      "question_type": "mcq",
      "topic": "Specific Topic Name",
      "difficulty": "beginner",
      "question_text": "Clear concise question text",
      "option_a": "First option text",
      "option_b": "Second option text",
      "option_c": "Third option text",
      "option_d": "Fourth option text",
      "correct_option": "a",
      "explanation": "Why this answer is correct"
    }},
    ...
    {{
      "order": 7,
      "question_type": "rating",
      "topic": "Practical Application",
      "difficulty": "self-assessment",
      "question_text": "Rate your comfort level executing...",
      "option_a": "1 - Beginner",
      "option_b": "2 - Learning",
      "option_c": "3 - Competent",
      "option_d": "4 - Expert",
      "correct_option": "",
      "explanation": "Self-assessment score"
    }}
  ]
}}
"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    llm_output = query_groq(messages, response_format_json=True, temperature=0.2, retries=1)

    if llm_output and validate_question_schema(llm_output):
        logger.info(f"Successfully generated dynamic assessment questions for '{cleaned_skill}' via Groq.")
        return llm_output.get('questions', [])

    logger.warning(f"Groq question generation unavailable or schema validation failed for '{cleaned_skill}'. Using curated fallback.")
    if 'python' in key:
        return CURATED_FALLBACK_BANK['python']
    return build_generic_fallback_questions(cleaned_skill)


def score_assessment(questions_with_answers: list) -> dict:
    """
    Score questions strictly on the server:
    - MCQs / Scenarios: correct = 100%, incorrect = 0%
    - Self-ratings: 1-5 scale mapped to 20%-100%
    Returns:
    {
      'score_percentage': float,
      'level': 'Beginner' | 'Intermediate' | 'Advanced',
      'strengths': list of topics,
      'gaps': list of topics,
      'summary': str
    }
    """
    total_weight = 0
    earned_weight = 0
    topic_scores = {}

    for item in questions_with_answers:
        q = item.get('question')
        ans = item.get('answer', '')
        rating = item.get('rating')

        topic = q.topic if hasattr(q, 'topic') and q.topic else (q.get('topic') if isinstance(q, dict) else 'General')
        q_type = q.question_type if hasattr(q, 'question_type') else (q.get('question_type') if isinstance(q, dict) else 'mcq')
        correct_opt = (q.correct_option if hasattr(q, 'correct_option') else (q.get('correct_option') if isinstance(q, dict) else '')).strip().lower()

        if topic not in topic_scores:
            topic_scores[topic] = {'earned': 0, 'possible': 0}

        if q_type == 'rating':
            weight = 1.0
            total_weight += weight
            topic_scores[topic]['possible'] += weight
            try:
                # 1 to 5 mapped to 0.2 to 1.0
                val = int(rating) if rating is not None else 3
                earned = max(1, min(5, val)) * 0.2
            except (ValueError, TypeError):
                earned = 0.5
            earned_weight += earned
            topic_scores[topic]['earned'] += earned
        else:
            weight = 2.0  # Objective questions carry higher weight
            total_weight += weight
            topic_scores[topic]['possible'] += weight
            user_opt = str(ans).strip().lower()
            if user_opt and user_opt == correct_opt:
                earned_weight += weight
                topic_scores[topic]['earned'] += weight

    score_pct = (earned_weight / total_weight * 100.0) if total_weight > 0 else 50.0
    score_pct = round(score_pct, 1)

    if score_pct < 45.0:
        level = 'Beginner'
    elif score_pct < 75.0:
        level = 'Intermediate'
    else:
        level = 'Advanced'

    strengths = []
    gaps = []

    for t, scores in topic_scores.items():
        if scores['possible'] > 0:
            pct = scores['earned'] / scores['possible']
            if pct >= 0.65:
                strengths.append(t)
            else:
                gaps.append(t)

    # Ensure at least one gap and strength for constructive balance
    if not strengths and gaps:
        strengths.append(gaps.pop(0))
    if not gaps:
        gaps.append("Production optimization and advanced architecture")

    summary = (
        f"Assessed at the {level} tier ({score_pct:.0f}%). "
        f"Demonstrated solid competency in {', '.join(strengths[:2])}. "
        f"Key focus areas for immediate growth include {', '.join(gaps[:2])}."
    )

    return {
        'score_percentage': score_pct,
        'level': level,
        'strengths': strengths,
        'gaps': gaps,
        'summary': summary
    }
