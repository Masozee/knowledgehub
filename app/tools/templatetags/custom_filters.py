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
