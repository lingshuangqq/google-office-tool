import re

def create_operation_plan(markdown_text: str) -> list:
    """Parses markdown into a list of operation blocks (simple text or table)."""
    plan = []
    lines = markdown_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|') and (i + 1) < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[i+1].strip()):
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
        
        simple_text_lines = []
        j = i
        while j < len(lines) and not (lines[j].strip().startswith('|') and (j + 1) < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[j+1].strip())):
            simple_text_lines.append(lines[j])
            j += 1
        
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

def find_table_and_get_cell_requests(doc_body: dict, table_rows: int, table_cols: int, cell_contents: list, expected_index: int):
    """Finds the table closest to the expected index and creates text insertion requests."""
    content = doc_body.get('content', [])
    best_match_table = None
    min_distance = float('inf')

    # Find the best matching table (the one closest to our insertion point)
    for element in content:
        if 'table' in element and element['table']['rows'] == table_rows and element['table']['columns'] == table_cols:
            distance = abs(element['startIndex'] - expected_index)
            if distance < min_distance:
                min_distance = distance
                best_match_table = element['table']

    if not best_match_table:
        return []

    # Now, generate requests for the best-matched table
    requests = []
    content_pointer = len(cell_contents) - 1
    for row in reversed(best_match_table.get('tableRows', [])):
        for cell in reversed(row.get('tableCells', [])):
            if content_pointer >= 0:
                if cell.get('content') and cell['content'][0].get('startIndex'):
                    cell_start_index = cell['content'][0]['startIndex']
                    text_to_insert = cell_contents[content_pointer]
                    if text_to_insert:
                        # Process cell content for inline styles (e.g., bold)
                        inline_requests, _ = handle_inline_styles(text_to_insert, cell_start_index)
                        requests.extend(inline_requests)
                content_pointer -= 1
    return requests

def get_simple_markdown_requests(markdown_text: str, start_index: int):
    """Generates API requests for a block of simple markdown text."""
    all_requests = []
    current_index = start_index
    lines = markdown_text.splitlines()
    for line in lines:
        requests, length = process_line_as_text(line, current_index)
        all_requests.extend(requests)
        current_index += length
    return all_requests, current_index - start_index

def process_line_as_text(line: str, start_index: int):
    requests = []
    is_list_item = False

    # Handle list items
    if line.strip().startswith('* ') or line.strip().startswith('- '):
        is_list_item = True
        # Determine the indentation level
        indentation_level = (len(line) - len(line.lstrip(' '))) / 2
        # Remove the bullet point and leading spaces from the line
        text_to_process = re.sub(r'^\s*[-*]\s*', '', line)
        header_style = None
    else:
        text_to_process, header_style = handle_paragraph_style(line)

    # Handle inline styles (bold, etc.)
    inline_requests, inserted_len = handle_inline_styles(text_to_process, start_index)
    requests.extend(inline_requests)

    # Add a newline character at the end of the line
    requests.append({'insertText': {'location': {'index': start_index + inserted_len}, 'text': '\n'}})
    total_len = inserted_len + 1

    # Apply heading style if applicable
    if header_style:
        requests.append({'updateParagraphStyle': {'range': {'startIndex': start_index, 'endIndex': start_index + total_len}, 'paragraphStyle': header_style, 'fields': 'namedStyleType'}})
    
    # Apply bullet point style if it's a list item
    if is_list_item:
        requests.append({
            'createParagraphBullets': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': start_index + total_len
                },
                'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
            }
        })
        # Apply indentation if necessary
        if indentation_level > 0:
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': start_index + total_len
                    },
                    'paragraphStyle': {
                        'indentStart': {
                            'magnitude': 36 * indentation_level,
                            'unit': 'PT'
                        }
                    },
                    'fields': 'indentStart'
                }
            })

    return requests, total_len

def handle_paragraph_style(line: str):
    if line.startswith('# '): return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '): return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '): return line[4:], {'namedStyleType': 'HEADING_3'}
    if line.startswith('#### '): return line[5:], {'namedStyleType': 'HEADING_4'}
    return line, None

def handle_inline_styles(text: str, start_index: int):
    """
    Correctly handles inline bold styling, overriding any inherited document styles.
    It inserts the clean text first, then applies `bold: true` or `bold: false`
    to the respective text segments.
    """
    requests = []
    clean_text = ""
    
    # This list will store tuples of (start, end, is_bold)
    segments = []
    
    last_end = 0
    for match in re.finditer(r'\*\*(.*?)\*\*', text):
        # Plain segment before the bold
        plain_before_text = text[last_end:match.start()]
        if plain_before_text:
            start_idx = len(clean_text)
            clean_text += plain_before_text
            end_idx = len(clean_text)
            segments.append((start_idx, end_idx, False))

        # Bold segment
        bold_content = match.group(1)
        if bold_content:
            start_idx = len(clean_text)
            clean_text += bold_content
            end_idx = len(clean_text)
            segments.append((start_idx, end_idx, True))
        
        last_end = match.end()
    
    # Final plain segment
    plain_after_text = text[last_end:]
    if plain_after_text:
        start_idx = len(clean_text)
        clean_text += plain_after_text
        end_idx = len(clean_text)
        segments.append((start_idx, end_idx, False))

    if not clean_text:
        return [], 0
    
    # 1. Insert the full clean text
    requests.append({'insertText': {'location': {'index': start_index}, 'text': clean_text}})
    
    # 2. Create style requests for all segments
    for start, end, is_bold in segments:
        if start == end: # Don't style empty segments
            continue
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index + start,
                    'endIndex': start_index + end
                },
                'textStyle': {
                    'bold': is_bold
                },
                'fields': 'bold'
            }
        })
        
    return requests, len(clean_text)