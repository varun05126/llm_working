import re
import html

def sanitize_and_normalize_markdown(text: str) -> str:
    """
    Normalizes markdown text and fixes legacy single-line database records.
    Strips internal model names and unwanted title preambles.
    """
    if not text:
        return ""

    text = str(text)

    # 1. Strip internal model names and title headers like:
    # "### Strategic AI Career Guidance (qwen/qwen3.8-27b):" or "(qwen/...)"
    text = re.sub(
        r'(?i)#{1,4}\s*Strategic AI Career Guidance\s*(\([^)]+\))?:?',
        '',
        text
    )
    text = re.sub(
        r'(?i)\bStrategic AI Career Guidance\s*(\([^)]+\))?:?',
        '',
        text
    )
    text = re.sub(
        r'\((?:qwen|openai|llama|deepseek|groq)[^)]*\)',
        '',
        text
    )

    # 2. Repair single-line legacy records where headings appear mid-line
    # Insert line break before any heading marker appearing inline
    text = re.sub(r'([^\n])\s+(#{1,4}\s+)', r'\1\n\n\2', text)

    # 3. Repair inline list bullets appearing mid-line after a colon or period
    # e.g., "Prerequisites: * Python basics * Git" -> "Prerequisites:\n* Python basics\n* Git"
    text = re.sub(r'([.:;])\s+([*+-]|\d+\.)\s+', r'\1\n\2 ', text)
    # Consecutive inline bullets: "item 1 * item 2" -> "item 1\n* item 2"
    text = re.sub(r'([^\n])\s+([*+-]|\d+\.)\s+([A-Z0-9a-z])', r'\1\n\2 \3', text)

    # 4. Remove awkward legacy intro sentence where goal and skill were mixed:
    text = re.sub(
        r'Tailored skill development strategy designed for [^.]+\.\s*Calculated based on your current assessment[^.]*\.\s*',
        '',
        text
    )

    return text.strip()


def render_markdown(text: str) -> str:
    """
    Safe, zero-dependency Markdown-to-HTML converter.
    Enforces strict HTML-escaping on all input first, preventing XSS.
    Only allows links beginning with http:// or https://.
    """
    if not text:
        return ""

    normalized = sanitize_and_normalize_markdown(text)
    if not normalized:
        return ""

    # Fenced code blocks extraction before line-by-line escaping
    # We match ```[lang]\ncode\n```
    code_blocks = []
    def save_code_block(match):
        code_content = match.group(2)
        # HTML-escape the raw code inside code block
        escaped_code = html.escape(code_content, quote=True).strip()
        idx = len(code_blocks)
        code_blocks.append(f'<pre><code>{escaped_code}</code></pre>')
        return f"\n\n__CODE_BLOCK_{idx}__\n\n"

    # Pattern for fenced code blocks
    normalized = re.sub(r'```([a-zA-Z0-9_-]*)\n?(.*?)```', save_code_block, normalized, flags=re.DOTALL)

    lines = normalized.split('\n')
    output_html = []
    in_ul = False
    in_ol = False
    in_blockquote = False
    blockquote_lines = []
    paragraph_lines = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            content = ' '.join(paragraph_lines).strip()
            if content:
                output_html.append(f'<p>{process_inlines(content)}</p>')
            paragraph_lines = []

    def flush_list():
        nonlocal in_ul, in_ol
        if in_ul:
            output_html.append('</ul>')
            in_ul = False
        if in_ol:
            output_html.append('</ol>')
            in_ol = False

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if in_blockquote and blockquote_lines:
            inner_text = '\n'.join(blockquote_lines)
            output_html.append(f'<blockquote>{render_markdown(inner_text)}</blockquote>')
            in_blockquote = False
            blockquote_lines = []

    for raw_line in lines:
        line = raw_line.strip()

        # Check for placeholder code block
        code_match = re.match(r'^__CODE_BLOCK_(\d+)__$', line)
        if code_match:
            flush_paragraph()
            flush_list()
            flush_blockquote()
            b_idx = int(code_match.group(1))
            if b_idx < len(code_blocks):
                output_html.append(code_blocks[b_idx])
            continue

        # Blank line
        if not line:
            flush_paragraph()
            flush_list()
            flush_blockquote()
            continue

        # Blockquote: starts with '>'
        if line.startswith('>'):
            flush_paragraph()
            flush_list()
            in_blockquote = True
            bq_content = line.lstrip('>').strip()
            blockquote_lines.append(bq_content)
            continue
        elif in_blockquote:
            flush_blockquote()

        # Horizontal rule: '---' or '***' or '___'
        if re.match(r'^(?:-{3,}|\*{3,}|_{3,})$', line):
            flush_paragraph()
            flush_list()
            output_html.append('<hr>')
            continue

        # Headings: #, ##, ###, ####
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            heading_text = process_inlines(html.escape(heading_match.group(2).strip(), quote=True))
            output_html.append(f'<h{level}>{heading_text}</h{level}>')
            continue

        # Unordered list: '-', '*', '+'
        ul_match = re.match(r'^[-*+]\s+(.+)$', line)
        if ul_match:
            flush_paragraph()
            if in_ol:
                flush_list()
            if not in_ul:
                output_html.append('<ul>')
                in_ul = True
            item_text = process_inlines(html.escape(ul_match.group(1).strip(), quote=True))
            output_html.append(f'<li>{item_text}</li>')
            continue

        # Ordered list: '1. ', '2. ', etc.
        ol_match = re.match(r'^\d+\.\s+(.+)$', line)
        if ol_match:
            flush_paragraph()
            if in_ul:
                flush_list()
            if not in_ol:
                output_html.append('<ol>')
                in_ol = True
            item_text = process_inlines(html.escape(ol_match.group(1).strip(), quote=True))
            output_html.append(f'<li>{item_text}</li>')
            continue

        # Regular text line belonging to a paragraph
        flush_list()
        # Escape the raw line before appending to paragraph
        escaped_line = html.escape(line, quote=True)
        paragraph_lines.append(escaped_line)

    flush_paragraph()
    flush_list()
    flush_blockquote()

    return '\n'.join(output_html)


def process_inlines(text: str) -> str:
    """
    Converts inline Markdown syntax (code, bold, italic, links) on an already HTML-escaped string.
    """
    if not text:
        return ""

    # Inline code: `code`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic: *text* or _text_
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text)

    # Links: [label](url)
    def render_link(match):
        label = match.group(1)
        raw_url = match.group(2).strip()
        # HTML unescape raw_url in case quote=True escaped &amp;
        unescaped_url = html.unescape(raw_url).strip()
        # Strict validation: ONLY allow http:// and https:// URLs!
        if re.match(r'^https?://', unescaped_url, re.IGNORECASE):
            safe_href = html.escape(unescaped_url, quote=True)
            return f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer">{label}</a>'
        # Disallowed / dangerous schemes (javascript:, data:, vbscript:, etc.) are rendered as safe text
        return f'{label} ({html.escape(unescaped_url, quote=True)})'

    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', render_link, text)

    return text
