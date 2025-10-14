# H1: Comprehensive Test Document

This document tests all supported formatting features of the Markdown-to-Google-Docs converter.

## H2: Text Formatting

This is a regular paragraph. Here is some **bold text**. And here is a mix of **bold** and plain text.

这是中文，这里有**加粗的中文**。

### H3: Lists

This section tests lists.
* Item 1
* Item 2
* **Item 3 with bold text**

### H3: Link Formatting

This section tests the new link support.
* A link to the project's guide: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
* A plain link to [Google](https://www.google.com).

#### H4: Another Level Down

Just to test the H4 heading.

## H2: Table Support

Below is a simple table.

| Header 1 | Header 2 | Header 3 |
|----------|:--------:|----------|
| Row 1, Col 1 | Row 1, Col 2 | Row 1, Col 3 |
| Row 2, Col 1 | Row 2, Col 2 | Row 2, Col 3 |
| **Bold** | `code` | [Google](https://google.com) |

Here is some text between two tables. This is important to ensure the parser correctly separates content blocks.

And here is a second, more complex table.

| Product | Feature | Status | Notes |
|---|---|:---:|---|
| Docs Converter | Bold Text | **Fixed** | Required explicit styling. |
| Docs Converter | Links | **Supported** | This is a test of that support. |
| Docs Converter | Tables | Supported | This is a test of that support. |
| Slides Converter| Protocol | Defined | See the [protocol file](src/google_slider/PROTOCOL.md). |