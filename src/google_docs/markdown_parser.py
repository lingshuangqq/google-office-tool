import re

def create_operation_plan(markdown_text: str) -> list:
    """Parses markdown into a list of operation blocks (simple text, table, or list)."""
    plan = []
    lines = markdown_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for Table
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

        # Check for List
        list_type = get_list_type(line)
        if list_type:
            list_lines = []
            j = i
            while j < len(lines):
                next_line = lines[j]
                next_type = get_list_type(next_line)
                # Continue if it's a list item.
                if next_type:
                    list_lines.append(next_line)
                    j += 1
                else:
                    break
            
            plan.append({'type': 'list', 'lines': list_lines, 'list_type': list_type})
            i = j
            continue
        
        # Simple Text
        simple_text_lines = []
        j = i
        while j < len(lines):
            # Stop if we hit a table or a list
            if (lines[j].strip().startswith('|') and (j + 1) < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[j+1].strip())):
                break
            if get_list_type(lines[j]):
                break
            
            simple_text_lines.append(lines[j])
            j += 1
        
        if any(line.strip() for line in simple_text_lines):
            plan.append({'type': 'simple', 'content': '\n'.join(simple_text_lines)})
        i = j

    return plan

def get_list_type(line: str):
    """Determines if a line is a list item and returns its type ('unordered' or 'ordered')."""
    stripped = line.strip()
    if re.match(r'^[-*]\s+', stripped):
        return 'unordered'
    if re.match(r'^\d+\.\s+', stripped):
        return 'ordered'
    return None

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

def get_list_requests(list_lines: list, list_type: str, start_index: int):
    """Generates API requests for a list block."""
    requests = []
    current_index = start_index
    
    for line in list_lines:
        # Calculate indentation (assuming 2 spaces = 1 level)
        leading_spaces = len(line) - len(line.lstrip(' '))
        indent_level = leading_spaces // 2
        
        # Content without marker
        # Dynamically check for marker type to handle nested mixed lists (e.g. unordered inside ordered)
        stripped_line = line.strip()
        if re.match(r'^[-*]\s+', stripped_line):
            content = re.sub(r'^\s*[-*]\s+', '', line)
        elif re.match(r'^\d+\.\s+', stripped_line):
            content = re.sub(r'^\s*\d+\.\s+', '', line)
        else:
            # Fallback (should typically not be reached for valid list lines)
            content = stripped_line
            
        # 1. Insert Tabs for nesting
        if indent_level > 0:
            requests.append({
                'insertText': {
                    'location': {'index': current_index},
                    'text': '\t' * indent_level
                }
            })
            current_index += indent_level
            
        # 2. Insert Content with Styles
        inline_reqs, inserted_len = handle_inline_styles(content, current_index)
        requests.extend(inline_reqs)
        current_index += inserted_len
        
        # 3. Insert Newline
        requests.append({
            'insertText': {
                'location': {'index': current_index},
                'text': '\n'
            }
        })
        current_index += 1

    # 4. Apply Bullets to the whole block
    total_len = current_index - start_index
    bullet_preset = 'BULLET_DISC_CIRCLE_SQUARE' if list_type == 'unordered' else 'NUMBERED_DECIMAL_ALPHA_ROMAN'
    
    requests.append({
        'createParagraphBullets': {
            'range': {
                'startIndex': start_index,
                'endIndex': current_index
            },
            'bulletPreset': bullet_preset
        }
    })
    
    return requests, total_len

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
    
    return requests, total_len

def handle_paragraph_style(line: str):
    if line.startswith('# '): return line[2:], {'namedStyleType': 'HEADING_1'}
    if line.startswith('## '): return line[3:], {'namedStyleType': 'HEADING_2'}
    if line.startswith('### '): return line[4:], {'namedStyleType': 'HEADING_3'}
    if line.startswith('#### '): return line[5:], {'namedStyleType': 'HEADING_4'}
    return line, None

def utf16_len(s: str) -> int:
    """Calculates the length of a string in UTF-16 code units."""
    return len(s.encode('utf-16-le')) // 2

def handle_inline_styles(text: str, start_index: int):
    """
    Correctly handles multiple and nested inline styles like bold, links, and inline code,
    overriding any inherited document styles by explicitly styling every text segment.
    """
    requests = []
    
    # Regex to find all markdown tokens (bold, link, or inline code)
    token_regex = r'(\*\*(?:.*?)\*\*|\[[^\]]+\]\([^\)]+\)|`(?:.*?)`)'
    parts = re.split(token_regex, text)
    
    current_pos = start_index
    for part in parts:
        if not part:
            continue

        # The logic is now more complex to handle nesting, specifically links inside bold.
        # We can't just use a simple if/elif chain on the whole part.

        # Is the part a bold token?
        bold_match = re.fullmatch(r'\*\*(?P<text>.*?)\*\*', part)
        if bold_match:
            bold_content = bold_match.group('text')
            # Now, recursively handle styles within the bold content
            # This is a simplified recursion: we just check for links inside.
            link_in_bold_match = re.match(r'^(.*?)(\[[^\]]+\]\([^\)]+\))(.*?)', bold_content)
            if link_in_bold_match:
                # Handle text before, the link, and text after, all as bold
                before_text, link_token, after_text = link_in_bold_match.groups()
                
                # 1. Text before link (bold)
                if before_text:
                    u16_len = utf16_len(before_text)
                    requests.append({'insertText': {'location': {'index': current_pos}, 'text': before_text}})
                    requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + u16_len}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
                    current_pos += u16_len

                # 2. The link itself (bold and linked)
                if link_token:
                    link_full_match = re.fullmatch(r'\[(?P<text>[^\]]+)\]\((?P<url>[^\)]+)\)', link_token)
                    link_text = link_full_match.group('text')
                    link_url = link_full_match.group('url')
                    u16_len = utf16_len(link_text)
                    requests.append({'insertText': {'location': {'index': current_pos}, 'text': link_text}})
                    requests.append({
                        'updateTextStyle': {
                            'range': {'startIndex': current_pos, 'endIndex': current_pos + u16_len},
                            'textStyle': {'bold': True, 'link': {'url': link_url}},
                            'fields': 'bold,link'
                        }
                    })
                    current_pos += u16_len

                # 3. Text after link (bold)
                if after_text:
                    u16_len = utf16_len(after_text)
                    requests.append({'insertText': {'location': {'index': current_pos}, 'text': after_text}})
                    requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + u16_len}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
                    current_pos += u16_len
            else:
                # No nesting, just a simple bold token
                u16_len = utf16_len(bold_content)
                requests.append({'insertText': {'location': {'index': current_pos}, 'text': bold_content}})
                requests.append({'updateTextStyle': {'range': {'startIndex': current_pos, 'endIndex': current_pos + u16_len}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
                current_pos += u16_len
            continue

        # Is the part a link token (and not inside bold)?
        link_match = re.fullmatch(r'\[(?P<text>[^\]]+)\]\((?P<url>[^\)]+)\)', part)
        if link_match:
            content = link_match.group('text')
            style = {'link': {'url': link_match.group('url')}}
            fields = 'link'
        # Is the part an inline code token?
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
        
        u16_len = utf16_len(content)
        segment_start = current_pos
        segment_end = current_pos + u16_len
        
        # 2. Apply the determined style
        requests.append({
            'updateTextStyle': {
                'range': {'startIndex': segment_start, 'endIndex': segment_end},
                'textStyle': style,
                'fields': fields
            }
        })
        
        current_pos += u16_len
        
    return requests, (current_pos - start_index)