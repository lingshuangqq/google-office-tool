# H1: Comprehensive Test Document

This document tests all supported formatting features of the Markdown-to-Google-Docs converter.

## H2: Text Formatting

This is a regular paragraph. Here is some **bold text**.
This line includes `inline code` for testing.
这是中文，这里有**加粗的中文**和`some_code()`。

### H3: Lists

This section tests lists.
* Item 1
    * Item 11
* Item 2
    * Item 22
        * Item 222
* **Item 3 with bold text** and `code`.

### H3: Link Formatting

This section tests the new link support.
* A link to the project's guide: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
* A plain link to [Google](https://www.google.com).
* A bold link: **[Google](https://www.google.com)**

#### H4: Another Level Down

Just to test the H4 heading.

## H2: Table Support

Below is a simple table.

| Header 1 | Header 2 | Header 3 |
|----------|:--------:|----------|
| Row 1, Col 1 | Row 1, Col 2 | Row 1, Col 3 |
| Row 2, Col 1 | Row 2, Col 2 | Row 2, Col 3 |
| **Bold** | `code()` | [Google](https://google.com) |

Here is some text between two tables. This is important to ensure the parser correctly separates content blocks.

And here is a second, more complex table.

| Product | Feature | Status | Notes |
|---|---|:---:|---|
| Docs Converter | Bold Text | **Fixed** | Required explicit styling. |
| Docs Converter | Links | **Supported** | This is a test of that support. |
| Docs Converter | Inline Code | `Supported` | This is a test of that support. |
| Docs Converter | Tables | Supported | This is a test of that support. |
| Slides Converter| Protocol | Defined | See the [protocol file](src/google_slider/PROTOCOL.md). |

---

## H2: Ordered and Nested Lists Test

1.  语言模型 - 实时交互：
    * 顶级性能：Claude Opus 在输出端成本优势明显。
    * 中端主力：Gemini Pro 和 GPT-5 形成价格同盟，是市场性价比标杆。
    * 低端市场：GPT-5 mini/nano 凭借极具攻击性的定价，在轻量和微型应用中占据主导。

2.  语言模型 - 离线批量处理：
    * Google Gemini 是无可争议的领导者。其在所有模型层级上都提供了远低于竞争对手的批量处理价格，是任何需要大规模离线数据处理的企业的首选。

3.  视频模型：
    * 市场尚在初期，定价混乱但策略各异。Sora 2 在基础音视频内容上更便宜，而 Veo 3 在高质量制作上更具优势。

4.  图像模型：
    * Google 的 Gemini Image (nano-banana) 扮演了“价格破坏者”的角色，以极低成本抢占需要大规模生成图片的应用场景。

### H3: Multi-line List Item Test (List Continuation)

1. Vertex AI 生成式 AI 完整定价指南
https://cloud.google.com/vertex-ai/generative-ai/pricing

2. 预留吞吐量 (Provisioned Throughput) 购买与使用指南
https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput

3. 优先随用随付 (Priority PayGo) 配置说明
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/priority-paygo

---

## H2: New Features (v1.4.0)

### H3: Italic Support
This section tests the *italic text* support. 
* *This is an italic list item.*
* This is a sentence with *italic* and **bold** text combined.
* You can even have an *italic link to [Google](https://google.com)*.

### H3: Horizontal Rule Support
The line below is a horizontal rule generated from `---`:

---

The line below is a horizontal rule generated from `***`:

***

The line below is a horizontal rule generated from `___`:

___

### H3: Code Blocks Support

This tests `inline code` mixed with other text.

And below is a multi-line code block test:

```python
def hello_world():
    """This is a test function."""
    print("Hello, World!")
    return True
```

```json
{
  "project": "Google Office MCP Tool",
  "features": ["code blocks", "italics", "horizontal rules"],
  "status": "success"
}
```

*This is the end of the formatting test.*

### H3: Blockquote Support

Here is a blockquote test:

> This is a blockquote.
> It can span multiple lines.
> It should appear indented and slightly grayed out.
> **Bold** and *italic* inside quotes should still work.

End of blockquote test.

### H3: Manual Line Break Support

This paragraph has a<br>manual line break in it using `<br>`.
And another one using `<br/>`.
And a third one using `<br />`.

Here is a table testing `<br>` inside cells:

| Name | Description |
|---|---|
| Item A | First line.<br>Second line.<br>Third line. |
| Item B | Text with `<br/>` and `<br />`. |
| Item C | **Line 1**<br>*Line 2* |

