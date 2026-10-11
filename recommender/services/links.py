import logging
import urllib.parse
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 86400  # 24 hours in seconds

OFFICIAL_DOCS_MAP = {
    'python': ('Official Python Docs', 'https://docs.python.org/3/'),
    'javascript': ('MDN JavaScript Guide', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript'),
    'typescript': ('TypeScript Official Handbook', 'https://www.typescriptlang.org/docs/'),
    'react': ('React Official Documentation', 'https://react.dev/'),
    'django': ('Django Official Docs', 'https://docs.djangoproject.com/'),
    'vue': ('Vue.js Official Guide', 'https://vuejs.org/guide/introduction.html'),
    'sql': ('PostgreSQL Documentation', 'https://www.postgresql.org/docs/'),
    'postgres': ('PostgreSQL Documentation', 'https://www.postgresql.org/docs/'),
    'postgresql': ('PostgreSQL Documentation', 'https://www.postgresql.org/docs/'),
    'docker': ('Docker Documentation', 'https://docs.docker.com/'),
    'kubernetes': ('Kubernetes Documentation', 'https://kubernetes.io/docs/'),
    'aws': ('AWS Getting Started Docs', 'https://aws.amazon.com/getting-started/'),
    'git': ('Git Official Documentation', 'https://git-scm.com/doc'),
    'html': ('MDN Web Docs (HTML)', 'https://developer.mozilla.org/en-US/docs/Web/HTML'),
    'css': ('MDN Web Docs (CSS)', 'https://developer.mozilla.org/en-US/docs/Web/CSS'),
    'pytorch': ('PyTorch Official Documentation', 'https://pytorch.org/docs/'),
    'tensorflow': ('TensorFlow Documentation', 'https://www.tensorflow.org/learn'),
    'pandas': ('Pandas Documentation', 'https://pandas.pydata.org/docs/'),
    'numpy': ('NumPy User Guide', 'https://numpy.org/doc/stable/user/'),
    'node': ('Node.js Official Documentation', 'https://nodejs.org/en/docs/'),
    'figma': ('Figma Official Help Center', 'https://help.figma.com/'),
    'go': ('Go Official Documentation', 'https://go.dev/doc/'),
    'rust': ('The Rust Programming Language Book', 'https://doc.rust-lang.org/book/'),
}


def build_youtube_links(topic: str) -> list:
    """
    Return curated YouTube search link and live video results if YOUTUBE_API_KEY is available.
    Cached for 24h.
    """
    encoded = urllib.parse.quote_plus(topic)
    default_search = {
        'title': f'Search YouTube: "{topic}"',
        'url': f'https://www.youtube.com/results?search_query={encoded}',
        'channel': 'YouTube Search',
        'is_api_result': False
    }

    api_key = getattr(settings, 'YOUTUBE_API_KEY', '') or ''
    if not api_key:
        return [default_search]

    cache_key = f'yt_{encoded[:50]}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': f'{topic} tutorial course',
            'type': 'video',
            'maxResults': 3,
            'key': api_key
        }
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            items = res.json().get('items', [])
            results = []
            for item in items:
                video_id = item.get('id', {}).get('videoId')
                snippet = item.get('snippet', {})
                if video_id:
                    results.append({
                        'title': snippet.get('title', 'Video Tutorial'),
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'channel': snippet.get('channelTitle', 'YouTube'),
                        'is_api_result': True
                    })
            if results:
                cache.set(cache_key, results, CACHE_TTL)
                return results
    except Exception as e:
        logger.warning(f"YouTube API call failed for '{topic}': {e}")

    return [default_search]


def build_github_links(skill: str) -> list:
    """
    Return GitHub repo search link and real top-starred repositories if possible.
    Cached for 24h.
    """
    encoded = urllib.parse.quote_plus(skill)
    default_search = {
        'title': f'Top GitHub repos for {skill}',
        'url': f'https://github.com/search?q={encoded}&type=repositories',
        'description': f'Explore popular starter repositories, boilerplates, and awesome lists for {skill}.',
        'stars': None,
        'is_api_result': False
    }

    cache_key = f'gh_{encoded[:50]}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    headers = {'Accept': 'application/vnd.github.v3+json'}
    token = getattr(settings, 'GITHUB_TOKEN', '') or ''
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        url = f'https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page=3'
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            items = res.json().get('items', [])
            results = []
            for item in items:
                results.append({
                    'title': item.get('full_name', item.get('name', 'Repository')),
                    'url': item.get('html_url', f'https://github.com/search?q={encoded}'),
                    'description': item.get('description', '') or 'Top open-source project',
                    'stars': item.get('stargazers_count', 0),
                    'is_api_result': True
                })
            if results:
                cache.set(cache_key, results, CACHE_TTL)
                return results
    except Exception as e:
        logger.warning(f"GitHub API call failed for '{skill}': {e}")

    return [default_search]


def build_internship_links(skill: str, location: str = "") -> list:
    """
    Deterministic direct search links for internships on LinkedIn, Internshala, Indeed, Google Jobs.
    Honest labeling ('Search on LinkedIn', etc.).
    """
    loc_part = location.strip() if location else "Remote"
    query = f"{skill} intern"
    encoded_q = urllib.parse.quote_plus(query)
    encoded_loc = urllib.parse.quote_plus(loc_part)
    combined = urllib.parse.quote_plus(f"{query} {loc_part}")

    return [
        {
            'portal': 'LinkedIn Jobs',
            'title': f'Search LinkedIn: {query} ({loc_part})',
            'url': f'https://www.linkedin.com/jobs/search/?keywords={encoded_q}&location={encoded_loc}',
            'note': 'Filter by "Internship" & "Entry level" under Experience level.'
        },
        {
            'portal': 'Internshala',
            'title': f'Search Internshala: {skill} Internships',
            'url': f'https://internshala.com/internships/keywords-{urllib.parse.quote_plus(skill)}',
            'note': 'Curated student and early-career internship listings.'
        },
        {
            'portal': 'Indeed',
            'title': f'Search Indeed: {query}',
            'url': f'https://www.indeed.com/jobs?q={encoded_q}&l={encoded_loc}',
            'note': 'Set alert for newly posted intern & apprentice openings.'
        },
        {
            'portal': 'Google Jobs',
            'title': f'Search Google Jobs: {query}',
            'url': f'https://www.google.com/search?q={combined}+internship+jobs&ibp=htl;jobs',
            'note': 'Aggregated listings across job boards and company career sites.'
        }
    ]


def build_course_and_doc_links(skill: str) -> list:
    """
    Deterministic search URLs for Coursera, edX, freeCodeCamp, Khan Academy,
    plus official docs when the skill maps to one.
    """
    encoded = urllib.parse.quote_plus(skill)
    lower_skill = skill.lower()

    results = []

    # Check for direct official documentation mapping
    for key, (doc_title, doc_url) in OFFICIAL_DOCS_MAP.items():
        if key in lower_skill:
            results.append({
                'provider': 'Official Documentation',
                'title': doc_title,
                'url': doc_url,
                'type': 'Docs & Reference'
            })
            break

    results.extend([
        {
            'provider': 'freeCodeCamp',
            'title': f'Search freeCodeCamp for "{skill}"',
            'url': f'https://www.freecodecamp.org/news/search/?query={encoded}',
            'type': 'Free Tutorials & Guides'
        },
        {
            'provider': 'Coursera',
            'title': f'Search Coursera Courses: {skill}',
            'url': f'https://www.coursera.org/search?query={encoded}',
            'type': 'University MOOCs (Audit for Free)'
        },
        {
            'provider': 'edX',
            'title': f'Search edX Programs: {skill}',
            'url': f'https://www.edx.org/search?q={encoded}',
            'type': 'Verified Courseware'
        },
        {
            'provider': 'Khan Academy',
            'title': f'Search Khan Academy: {skill}',
            'url': f'https://www.khanacademy.org/search?page_search_query={encoded}',
            'type': 'Foundational Practice'
        }
    ])

    return results


def build_community_and_cert_links(skill: str) -> dict:
    """
    Communities, mentorship programs, scholarships for women in tech,
    and recognized certifications (free/paid).
    """
    communities = [
        {
            'name': 'Women Who Code',
            'url': 'https://www.womenwhocode.com/',
            'description': 'Global community supporting women excelling in technology careers with technical talks, tracks, and local chapters.'
        },
        {
            'name': 'AnitaB.org & Grace Hopper Celebration',
            'url': 'https://anitab.org/',
            'description': 'Scholarships, leadership networks, and the largest gathering of women technologists globally.'
        },
        {
            'name': 'Rewriting the Code',
            'url': 'https://rewritingthecode.org/',
            'description': 'Mentorship, university fellowships, and recruiting connections for collegiate women in tech.'
        },
        {
            'name': 'Ada\'s List',
            'url': 'https://www.adaslist.net/',
            'description': 'Global network for women and non-binary individuals in tech for collaboration, jobs, and mentorship.'
        }
    ]

    certs = [
        {
            'name': f'FreeCodeCamp {skill} Certification',
            'cost_type': 'Free',
            'url': f'https://www.freecodecamp.org/news/search/?query={urllib.parse.quote_plus(skill)}'
        },
        {
            'name': f'Coursera Professional Certificate in {skill}',
            'cost_type': 'Free Audit / Paid Cert',
            'url': f'https://www.coursera.org/search?query={urllib.parse.quote_plus(skill)}'
        },
        {
            'name': f'edX Verified Certificate in {skill}',
            'cost_type': 'Paid Option',
            'url': f'https://www.edx.org/search?q={urllib.parse.quote_plus(skill)}'
        }
    ]

    return {
        'communities': communities,
        'certifications': certs
    }
