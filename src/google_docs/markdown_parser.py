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
    Correctly handles multiple inline styles like bold, links, and inline code,
    overriding any inherited document styles by explicitly styling every text segment.
    """
    requests = []
    
    # Regex to find all markdown tokens (bold, link, or inline code)
    token_regex = r'(\*\*(?:.*?)\*\*|\[(?:.*?)\]\((?:.*?)\)|`(?:.*?)`)'
    parts = re.split(token_regex, text)
    
    current_pos = start_index
    for part in parts:
        if not part:
            continue

        # Check if the part is a bold token
        bold_match = re.fullmatch(r'\*\*(?P<text>.*?)\*\*', part)
        if bold_match:
            content = bold_match.group('text')
            style = {'bold': True}
            fields = 'bold'
        # Check if the part is a link token
        elif (link_match := re.fullmatch(r'\[(?P<text>.*?)\]\((?P<url>.*?)\)', part)):
            content = link_match.group('text')
            style = {'link': {'url': link_match.group('url')}}
            fields = 'link'
        # Check if the part is an inline code token
        elif (code_match := re.fullmatch(r'`(?P<text>.*?)`', part)):
            content = code_match.group('text')
            style = {
                'weightedFontFamily': {
                    'fontFamily': 'Courier New'
                },
                'backgroundColor': {
                    'color': {
                        'rgbColor': {
                            'red': 0.93, 'green': 0.93, 'blue': 0.93
                        }
                    }
                }
            }
            fields = 'weightedFontFamily,backgroundColor'
        # Otherwise, it's plain text
        else:
            content = part
            # Explicitly reset all styles for plain text to avoid inheritance
            style = {
                'bold': False,
                'italic': False,
                'underline': False,
                'strikethrough': False,
                'backgroundColor': {},
                'link': None,
                'weightedFontFamily': {
                    'fontFamily': 'Arial' # Reset font to a default
                }
            }
            fields = 'bold,italic,underline,strikethrough,backgroundColor,link,weightedFontFamily'

        if not content:
            continue

        # 1. Insert the text segment
        requests.append({'insertText': {'location': {'index': current_pos}, 'text': content}})
        
        segment_start = current_pos
        segment_end = current_pos + len(content)
        
        # 2. Apply the determined style
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': segment_start, 'endIndex': segment_end},
                'textStyle': style,
                'fields': fields
            }
        })
        
        current_pos += len(content)
        
    return requests, (current_pos - start_index)