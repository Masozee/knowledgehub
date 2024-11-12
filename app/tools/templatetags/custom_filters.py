from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='move_code_section')
def move_code_section(content):
    """
    Custom filter to extract code blocks wrapped in triple backticks and move them
    to a <pre><code>...</code></pre> section.
    """
    # Find all the code blocks wrapped with triple backticks
    code_blocks = re.findall(r'```(.*?)```', content, flags=re.DOTALL)

    # Replace the code blocks with placeholders in the content
    processed_content = re.sub(r'```(.*?)```', r'<div class="code-section"></div>', content, flags=re.DOTALL)

    # Generate separate HTML code sections for each code block
    code_section_html = ''
    for code_block in code_blocks:
        # Add the code block in a separate HTML structure
        code_section_html += f'<pre class="chat-code"><code>{code_block.strip()}</code></pre>'

    return mark_safe(processed_content + code_section_html)


@register.filter(name='format_markdown')
def format_markdown(content):
    """
    Handle Markdown-style formatting:
    - ### for headers
    - ** for bold text
    - Preserves existing HTML
    """
    if not content:
        return content

    # Temporarily replace existing HTML tags
    placeholder_map = {}

    def store_html(match):
        placeholder = f"__HTML_PLACEHOLDER_{len(placeholder_map)}__"
        placeholder_map[placeholder] = match.group(0)
        return placeholder

    content = re.sub(r'<[^>]+>', store_html, content)

    # Handle headers (###)
    content = re.sub(r'^###\s*(.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^##\s*(.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^#\s*(.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)

    # Handle bold text (**)
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)

    # Restore HTML placeholders
    for placeholder, html in placeholder_map.items():
        content = content.replace(placeholder, html)

    return mark_safe(content)


@register.filter
def format_transcript(content):
    """
    Formats transcript content with timestamps, Markdown, and code blocks
    """
    if not content:
        return content

    # First handle code blocks to prevent interference with other formatting
    content = move_code_section(content)

    # Then handle Markdown formatting
    content = format_markdown(content)

    return mark_safe(content)


@register.filter
def strip(value):
    """Strips whitespace from string"""
    return value.strip() if value else ''

@register.filter
def extract_timestamp(line):
    """Extracts timestamp from line in format [00:00:00 - 00:00:06]"""
    match = re.match(r'\[([\d:]+)\s*-\s*([\d:]+)\]', line)
    if match:
        start_time, end_time = match.groups()
        return f"{start_time} - {end_time}"
    return ''

@register.filter
def extract_text(line):
    """Extracts text after timestamp"""
    # Remove timestamp and any whitespace after it
    return re.sub(r'\[[\d:\s-]+\]\s*', '', line).strip()

@register.filter
def format_transcript(text):
    """Formats transcript text"""
    return text.strip()


@register.filter
def format_duration(seconds):
    """Formats duration in seconds to HH:MM:SS"""
    if not seconds:
        return "00:00:00"

    seconds = int(float(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@register.filter
def format_filesize(size):
    """Formats file size in bytes to human readable format"""
    try:
        size = float(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except (ValueError, TypeError):
        return "0 B"


@register.filter
def timestamp_to_seconds(timestamp):
    """
    Convert HH:MM:SS timestamp to seconds
    Example: "01:23:45" -> 5025
    """
    try:
        h, m, s = map(int, timestamp.split(':'))
        return h * 3600 + m * 60 + s
    except (ValueError, AttributeError):
        return 0


@register.filter
def get_duration_percent(timestamp, total_duration):
    """
    Get percentage of timestamp in total duration
    Example: "00:30:00", 3600 -> 50.0
    """
    try:
        seconds = timestamp_to_seconds(timestamp)
        return (seconds / float(total_duration)) * 100
    except (ValueError, ZeroDivisionError):
        return 0