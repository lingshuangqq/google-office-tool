import re

def create_operation_plan(markdown_text: str) -> list:
    """Parses markdown into a list of operation blocks (simple text or table)."""
    plan = []
    lines = markdown_text.splitlines()
    i = 0
    while i < len(lines):
        # Check if the current line is the start of a table
        if lines[i].strip().startswith('|') and (i + 1) < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[i+1].strip()):
            table_lines = []
            j = i
            while j < len(lines) and lines[j].strip().startswith('|'):
                table_lines.append(lines[j])
                j += 1
            
            table_markdown = '\n'.join(table_lines)
            table_data = parse_markdown_table(table_markdown)
            if table_data:
                plan.append({'type': 'table', 'data': table_data})
                i = j
                continue
        
        # If not a table, treat as a block of simple text
        simple_text_lines = []
        j = i
        # Collect all lines until the next table starts
        while j < len(lines) and not (lines[j].strip().startswith('|') and (j + 1) < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[j+1].strip())):
            simple_text_lines.append(lines[j])
            j += 1
        
        # Only add a block if it contains non-empty lines
        if any(line.strip() for line in simple_text_lines):
            plan.append({'type': 'simple', 'content': '\n'.join(simple_text_lines)})
        i = j

    return plan

def parse_markdown_table(markdown_text: str):
    """Parses a block of text known to be a table."""
    lines = [line.strip() for line in markdown_text.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    header_cells = [cell.strip() for cell in lines[0].strip('|').split('|')]
    num_columns = len(header_cells)
    if num_columns == 0:
        return None

    separator_line = lines[1].strip()
    if not re.match(r'^\|[-|: ]+\|$', separator_line):
        return None

    all_cell_contents = header_cells
    data_rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if len(cells) == num_columns:
            data_rows.append(cells)
            all_cell_contents.extend(cells)
        
    num_rows = len(data_rows) + 1
    return num_rows, num_columns, all_cell_contents

def find_table_and_get_cell_requests(doc_body: dict, table_rows: int, table_cols: int, cell_contents: list):
    """Finds the LAST table and creates text insertion requests in reverse order."""
    requests = []
    content = doc_body.get('content', [])
    
    for element in reversed(content):
        if 'table' in element and element['table']['rows'] == table_rows and element['table']['columns'] == table_cols:
            table = element['table']
            content_pointer = len(cell_contents) - 1
            for row in reversed(table.get('tableRows', [])):
                for cell in reversed(row.get('tableCells', [])):
                    if content_pointer >= 0:
                        if cell.get('content') and cell['content'][0].get('startIndex'):
                            cell_start_index = cell['content'][0]['startIndex']
                            text_to_insert = cell_contents[content_pointer]
                            if text_to_insert:
                                requests.append({'insertText': {'location': {'index': cell_start_index}, 'text': text_to_insert}})
                        content_pointer -= 1
            return requests
    return []

def get_simple_markdown_requests(markdown_text: str, start_index: int):
    """Generates API requests for a block of simple markdown text."""
    all_requests = []
    current_index = start_index
    lines = markdown_text.splitlines()
    for line in lines:
        requests, length = process_line_as_text(line, current_index)
        all_requests.extend(requests)
        current_index += length
    return all_requests, current_index - start_index # Return total length

def process_line_as_text(line: str, start_index: int):
    requests = []
    text_to_process, header_style = handle_paragraph_style(line)
    inline_requests, inserted_len = handle_inline_styles(text_to_process, start_index)
    requests.extend(inline_requests)
    requests.append({'insertText': {'location': {'index': start_index + inserted_len}, 'text': '\n'}})
    total_len = inserted_len + 1
    if header_style:
        requests.append({'updateParagraphStyle': {'range': {'startIndex': start_index, 'endIndex': start_index + total_len}, 'paragraphStyle': header_style, 'fields': 'namedStyleType'}})
    return requests, total_len

def handle_paragraph_style(line: str):
    if line.startswith('# '): return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '): return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '): return line[4:], {'namedStyleType': 'HEADING_3'}
    if line.startswith('#### '): return line[5:], {'namedStyleType': 'HEADING_4'}
    return line, None

def handle_inline_styles(text: str, start_index: int):
    requests = []
    current_pos = start_index
    last_end = 0
    matches = list(re.finditer(r'\*\*(.*?)\*\*', text))
    if not matches:
        if text:
            requests.append({'insertText': {'location': {'index': start_index}, 'text': text}})
        return requests, len(text)
    for match in matches:
        start, end = match.span()
        plain_before = text[last_end:start]
        if plain_before:
            requests.append({'insertText': {'location': {'index': current_pos}, 'text': plain_before}})
            current_pos += len(plain_before)
        bold_text = match.group(1)
        if bold_text:
            requests.append({'insertText': {'location': {'index': current_pos}, 'text': bold_text}})
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': current_pos, 'endIndex': current_pos + len(bold_text)},
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })
            current_pos += len(bold_text)
        last_end = end
    plain_after = text[last_end:]
    if plain_after:
        requests.append({'insertText': {'location': {'index': current_pos}, 'text': plain_after}})
    final_len = len(re.sub(r'\*\*', '', text))
    return requests, final_len
