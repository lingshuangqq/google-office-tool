# Google Office 工具

## 架构图

下图展示了本工具的核心架构和工作流程。用户通过命令行工具与程序交互，该工具会读取本地的 Markdown 文件和凭证，然后调用相应的 Google Workspace API 来创建或修改 Google Docs 文档和 Google Slides 演示文稿，并最终将它们保存在 Google Drive 中。

![Project Architecture](generated-diagrams/architecture.png)

本项目提供了一个命令行工具，用于将 Markdown 文件转换为 Google Docs 文档和 Google Slides 演示文稿。

## 环境准备

- Python 3.x
- 一个已启用 Google Docs API 和 Google Slides API 的 Google Cloud Platform 项目。

## 安装与配置

### 1. 安装依赖

使用 pip 安装所有必需的 Python 库：

```bash
pip install -r requirements.txt
```

### 2. 配置凭证

本工具支持两种 Google API 认证方式：

**a) OAuth 2.0 (推荐大多数用户使用):**

1.  前往 [Google Cloud Console](https://console.cloud.google.com/)。
2.  导航至 **API 与服务 > 凭据**。
3.  为 **桌面应用** 创建一个 **OAuth 2.0 客户端 ID**。
4.  下载凭证的 JSON 文件，并将其另存为 `code/credentials/oauth-credentials.json`。

首次运行工具时，系统会自动打开浏览器窗口，引导您登录并授权。成功后，一个 `token.json` 文件将被创建在 `code/credentials` 目录下，用于保存您的授权信息，以便后续使用。

**b) 服务账号 (Service Account):**

1.  在 Google Cloud Console 中，创建一个**服务账号**。
2.  授予该账号操作 Google Drive、Docs 和 Slides 的必要权限（例如：编辑者）。
3.  为服务账号创建一个密钥，并下载 JSON 文件。
4.  将文件另存为 `code/credentials/docs-writer-credentials.json`（或使用其他名称，并通过 `--sa_path` 参数指定）。

## 使用方法

所有操作都可以通过 `client.py` 命令行工具直接执行，也可以通过 `scripts/` 目录中封装好的辅助脚本来执行。

### 直接使用命令行工具 (`client.py`)

项目的主入口是 `code/src/client.py`。您可以从项目根目录直接调用它。

**基本命令结构:**
```bash
python3 code/src/client.py [工具] [命令] [参数]
```

#### Google Docs 工具 (`docs`)

- **创建新文档:**
  ```bash
  python3 code/src/client.py docs write <MARKDOWN_FILE> --title "<文档标题>" [--folder_id <文件夹ID>]
  ```

- **追加内容到文档:**
  ```bash
  python3 code/src/client.py docs append <DOC_ID> "<要追加的文本>"
  python3 code/src/client.py docs append <DOC_ID> --file <MARKDOWN_FILE>
  ```

- **替换占位符:**
  ```bash
  python3 code/src/client.py docs replace <DOC_ID> <占位符文本> <MARKDOWN_FILE>
  ```

- **清空文档:**
  ```bash
  python3 code/src/client.py docs clear <DOC_ID>
  ```

#### Google Slides 工具 (`slides`)

- **创建新演示文稿:**
  ```bash
  python3 code/src/client.py slides create <MARKDOWN_FILE> [--title "<演示文稿标题>"] [--folder_id <文件夹ID>] [--template_id <模板ID>]
  ```

### 使用封装脚本

为了方便使用，您可以直接运行 `code/scripts/` 目录下的 shell 脚本。

#### 文档操作脚本

- **创建新文档:**
  ```bash
  bash code/scripts/run_create_doc.sh "<标题>" "<Markdown文件路径>" [文件夹ID]
  ```

- **追加文本到文档:**
  ```bash
  bash code/scripts/run_append.sh <文档ID> "<要追加的文本>"
  ```

- **从文件追加内容到文档:**
  ```bash
  bash code/scripts/run_markdown_append.sh <文档ID> <Markdown文件路径>
  ```

- **替换文档中的占位符:**
  ```bash
  bash code/scripts/run_replace_placeholders.sh <文档ID> <占位符> <Markdown文件路径>
  ```

- **清空文档:**
  ```bash
  bash code/scripts/run_clear_doc.sh <文档ID>
  ```

#### 演示文稿操作脚本

- **创建新演示文稿:**
  ```bash
  bash code/scripts/run_create_presentation.sh <Markdown文件路径> [文件夹ID] [模板ID] "[标题]"
  ```

## Markdown 格式协议

- **Google Docs:** 用于生成文档的 Markdown 解析器支持标题、粗体和列表。更多细节请参考 `code/src/google_docs/markdown_parser.py` 中的实现。
- **Google Slides:** 用于生成演示文稿的 Markdown 遵循特定的协议来定义幻灯片、标题和内容。详细规范请参阅此处的文档：[Google Slides Markdown 协议](src/google_slider/PROTOCOL.md)。