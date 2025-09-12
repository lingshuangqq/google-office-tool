import os.path
import argparse
import re
from googleapiclient.errors import HttpError

def format_text(shape_id, text, font_size):
    requests = []
    plain_text = text.replace('**', '')
    requests.append({
        'insertText': {
            'objectId': shape_id,
            'text': plain_text,
            'insertionIndex': 0
        }
    })

    # Set the font size for the whole text
    requests.append({
        'updateTextStyle': {
            'objectId': shape_id,
            'style': {
                'fontSize': {
                    'magnitude': font_size,
                    'unit': 'PT'
                }
            },
            'fields': 'fontSize'
        }
    })

    offset = 0
    for match in re.finditer(r'\*\*(.*?)\*\*', text):
        start = match.start(1) - offset - 2
        end = match.end(1) - offset - 2
        requests.append({
            'updateTextStyle': {
                'objectId': shape_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': start,
                    'endIndex': end
                },
                'style': {
                    'bold': True
                },
                'fields': 'bold'
            }
        })
        offset += 4
    return requests

def create_presentation_from_markdown(services, markdown_file, drive_folder_id=None, template_id=None, title=None):
    """Creates a Google Slides presentation from a markdown file."""
    try:
        with open(markdown_file, 'r') as f:
            content = f.read()

        slides_content = content.split('---\n')
        
        if len(slides_content) > 0 and slides_content[0].strip() == "":
            slides_content.pop(0)

        if title:
            presentation_title = title
        elif slides_content:
            first_slide_lines = slides_content[0].strip().split('\n')
            for line in first_slide_lines:
                if line.startswith("标题："):
                    presentation_title = line.replace("标题：", "").strip()
                    break

        slides_service = services["slides"]
        drive_service = services["drive"]

        if template_id:
            body = {'name': presentation_title}
            presentation = drive_service.files().copy(fileId=template_id, body=body).execute()
            presentation_id = presentation.get('id')
            presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
            slide_ids = [slide.get('objectId') for slide in presentation.get('slides')]
            requests = []
            for slide_id in slide_ids:
                requests.append({
                    'deleteObject': {
                        'objectId': slide_id
                    }
                })
            if requests:
                slides_service.presentations().batchUpdate(
                    presentationId=presentation_id, body={'requests': requests}
                ).execute()
        else:
            body = {"title": presentation_title}
            presentation = (
                slides_service.presentations().create(body=body).execute()
            )
            presentation_id = presentation.get('presentationId')
            requests = [
                {
                    'deleteObject': {
                        'objectId': presentation.get('slides')[0].get('objectId')
                    }
                }
            ]
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={'requests': requests}
            ).execute()

        
        print(f"Created presentation with ID: {presentation_id}")

        if drive_folder_id:
            file = drive_service.files().get(fileId=presentation_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            drive_service.files().update(
                fileId=presentation_id,
                addParents=drive_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

        slide_index = 0
        for i, slide_content in enumerate(slides_content):
            slide_content = slide_content.strip()
            if not slide_content:
                continue

            lines = slide_content.split('\n')
            title = ""
            subtitle = ""
            body_text = ""
            image_path = ""
            core_idea = ""

            for line in lines:
                if line.startswith("标题："):
                    title = line.replace("标题：", "").strip()
                elif line.startswith("副标题："):
                    subtitle = line.replace("副标题：", "").strip()
                elif line.startswith("正文："):
                    body_text += line.replace("正文：", "") + '\n' 
                elif line.startswith("图片："):
                    image_path = line.replace("图片：", "").strip() 
                elif line.startswith("核心思想："):
                    core_idea = line.replace("核心思想：", "").strip() 
                else: 
                    body_text += line + '\n'
            
            body_text = body_text.strip()

            layout = 'TITLE_AND_BODY'
            if i == 0:
                layout = 'TITLE'
            elif subtitle:
                layout = 'SECTION_HEADER'

            requests = [
                {
                    'createSlide': {
                        'insertionIndex': str(slide_index),
                        'slideLayoutReference': {
                            'predefinedLayout': layout
                        }
                    }
                }
            ]

            try:
                response = slides_service.presentations().batchUpdate(
                    presentationId=presentation_id, body={'requests': requests}
                ).execute()
            except HttpError as e:
                if "The predefined layout" in str(e) and "is not present" in str(e):
                    print(f"Layout {layout} not found, falling back to TITLE_AND_BODY")
                    requests[0]['createSlide']['slideLayoutReference']['predefinedLayout'] = 'TITLE_AND_BODY'
                    response = slides_service.presentations().batchUpdate(
                        presentationId=presentation_id, body={'requests': requests}
                    ).execute()
                else:
                    raise e

            slide_id = response['replies'][0]['createSlide']['objectId']
            slide = slides_service.presentations().pages().get(presentationId=presentation_id, pageObjectId=slide_id).execute()
            title_shape_id = None
            subtitle_shape_id = None
            body_shape_id = None
            for shape in slide.get('pageElements', []):
                placeholder_type = shape.get('shape', {}).get('placeholder', {}).get('type')
                if i == 0:
                    if placeholder_type == 'CENTERED_TITLE':
                        title_shape_id = shape['objectId']
                    elif placeholder_type == 'SUBTITLE':
                        subtitle_shape_id = shape['objectId']
                else:
                    if placeholder_type == 'TITLE':
                        title_shape_id = shape['objectId']
                    elif placeholder_type == 'BODY':
                        if layout == 'SECTION_HEADER':
                            subtitle_shape_id = shape['objectId']
                        else:
                            body_shape_id = shape['objectId']
            
            requests = []
            if title_shape_id and title:
                requests.extend(format_text(title_shape_id, title, 32))

            if i == 0:
                full_subtitle = ""
                if subtitle:
                    full_subtitle += subtitle + '\n'
                if body_text:
                    full_subtitle += body_text + '\n'
                if core_idea:
                    full_subtitle += core_idea
                if subtitle_shape_id and full_subtitle:
                    requests.extend(format_text(subtitle_shape_id, full_subtitle.strip(), 16))
            else:
                if subtitle_shape_id and subtitle:
                    requests.extend(format_text(subtitle_shape_id, subtitle, 16))
                if body_shape_id and body_text:
                    requests.extend(format_text(body_shape_id, body_text, 16))

            if requests:
                slides_service.presentations().batchUpdate(
                    presentationId=presentation_id, body={'requests': requests}
                ).execute()
            
            slide_index += 1

        return presentation

    except Exception as error:
        print(f"An error occurred: {error}")
        return None
