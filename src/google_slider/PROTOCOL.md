# Google Slides Markdown Protocol

This document outlines the Markdown protocol used to generate Google Slides presentations.

## 1. Slide Separation

Each slide in the Markdown file is separated by a horizontal rule (`---`).

## 2. Key-Value Pairs

Each slide is defined by a set of key-value pairs. The following keys are supported:

- `标题：<slide_title>`: Specifies the title of the slide.
- `副标题：<slide_subtitle>`: Specifies the subtitle of the slide. The presence of this key will trigger the use of the "Section Header" layout.
- `正文：<slide_body>`: Defines the body content of the slide. 
    - Multiple `正文：` lines can be used and will be concatenated.
    - Basic bold formatting with `**text**` is supported.
- `核心思想：<core_idea>`: Used only for the first slide (the title slide). This text will be appended to the subtitle section.
- `图片：<image_path>`: Specifies an image to be inserted into the slide. (Note: Image insertion is not yet fully implemented in the script).

## 3. Layouts

The script automatically selects the slide layout based on the provided keys:

- **Title Slide**: The very first slide of the presentation will always use the `TITLE` layout. 
    - The `标题：` key sets the main title.
    - The content from `副标题：`, `正文：`, and `核心思想：` will be combined to form the subtitle.
- **Section Header**: Any slide (other than the first) that contains a `副标题：` key will use the `SECTION_HEADER` layout. For these slides, the `正文：` and `图片：` keys are ignored.
- **Title and Body**: All other slides will use the `TITLE_AND_BODY` layout.

## 4. Sample Markdown

```markdown
---
标题：协议演示
副标题：一个完整的示例
核心思想：这是一个核心思想
---
标题：简单的幻灯片
正文：这是幻灯片的第一行。
正文：这是**粗体**的第二行。
---
标题：带图片的幻灯片
图片：images/sample_image.png
---
标题：只有标题的幻灯片
---
标题：带正文和图片的幻灯片
正文：这张幻灯片既有文字，又有图片。
图片：images/another_image.png
---
```
