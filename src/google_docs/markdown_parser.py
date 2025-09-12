import re

# --- Markdown Parsing and Request Generation ---

def get_markdown_requests(markdown_text: str, start_index: int):
    """Converts a markdown string into a list of Google Docs API requests starting at a given index."""
    all_requests = []
    current_index = start_index
    lines = markdown_text.split('\n')

    for line in lines:
        line_start_index = current_index
        
        # 1. Handle Paragraph Styles (Headers, Lists)
        indent_level, list_text, bullet_char = handle_list_item(line)
        if list_text is not None:
            text_to_process = bullet_char + ' ' + list_text
            paragraph_style = {
                'indentFirstLine': {'magnitude': 18 * (indent_level + 1), 'unit': 'PT'},
                'indentStart': {'magnitude': 36 * (indent_level + 1), 'unit': 'PT'}
            }
            paragraph_fields = 'indentStart,indentFirstLine'
        else:
            text_to_process, header_style = handle_paragraph_style(line)
            paragraph_style = header_style
            paragraph_fields = 'namedStyleType'

        # 2. Handle Inline Styles (Bold)
        inline_requests, inserted_len = handle_inline_styles(text_to_process, current_index)
        all_requests.extend(inline_requests)
        current_index += inserted_len

        # 3. Add newline and apply paragraph style
        all_requests.append({'insertText': {'location': {'index': current_index}, 'text': '\n'}})
        current_index += 1
        if paragraph_style:
            all_requests.append({
                'updateParagraphStyle': {
                    'range': {'startIndex': line_start_index, 'endIndex': current_index},
                    'paragraphStyle': paragraph_style,
                    'fields': paragraph_fields
                }
            })

    return all_requests

def handle_paragraph_style(line: str):
    if line.startswith('# '): return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '): return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '): return line[4:], {'namedStyleType': 'HEADING_3'}
    if line.startswith('#### '): return line[5:], {'namedStyleType': 'HEADING_4'}
    return line, None

def handle_list_item(line: str):
    match = re.match(r'^(\s*)(\*|-)\s+(.*)', line)
    if not match: return None, None, None
    indent_str, text = match.group(1), match.group(3)
    indent_level = len(indent_str) // 2
    bullet_chars = ['\u25CF', '\u25CB', '\u25A0']
    bullet_char = bullet_chars[indent_level % len(bullet_chars)]
    return indent_level, text, bullet_char

def handle_inline_styles(text: str, start_index: int):
    requests = []
    matches = list(re.finditer(r'\*\*(.*?)\*\*', text))
    last_end, current_pos = 0, start_index
    clean_text_len = len(re.sub(r'\*\*', '', text))

    if not matches:
        if text: requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': text}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(text)}, 'textStyle': {'bold': False}, 'fields': 'bold'}}])
        return requests, len(text)

    for match in matches:
        start, end = match.span()
        # Plain text before bold
        plain_before = text[last_end:start]
        if plain_before:
            requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': plain_before}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(plain_before)}, 'textStyle': {'bold': False}, 'fields': 'bold'}}])
            current_pos += len(plain_before)
        # Bold text
        bold_text = match.group(1)
        if bold_text:
            requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': bold_text}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(bold_text)}, 'textStyle': {'bold': True}, 'fields': 'bold'}}])
            current_pos += len(bold_text)
        last_end = end
    # Plain text after last bold
    plain_after = text[last_end:]
    if plain_after:
        requests.extend([{'insertText': {'location': {'index': current_pos}, 'text': plain_after}}, {'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + len(plain_after)}, 'textStyle': {'bold': False}, 'fields': 'bold'}}])
    return requests, clean_text_len
