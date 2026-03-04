# Google Office Tool MCP 服务器

本文件提供有关如何设置和使用 Google Office Tool MCP 服务器的说明。该服务器将所有 Google Office 功能封装为一套本地工具，可供 Gemini CLI 或 Cursor 等兼容 MCP 协议的 AI 助手调用。

## 先决条件

在您使用此工具之前，您需要设置您的 Google Cloud 项目并创建 OAuth 2.0 凭据。

1.  **Google Cloud 项目**:
    *   确保您有一个 Google Cloud 项目。
    *   为您的项目启用 **Google Docs API** 和 **Google Slides API**。

2.  **OAuth 2.0 凭据**:
    *   为“桌面应用程序”创建 OAuth 2.0 凭据。
    *   将凭据下载为 JSON 文件，并将其放置在项目根目录的 `credentials/` 文件夹中，重命名为 `oauth-credentials.json`。

## 认证

*   首次运行工具时，系统会自动启动 OAuth 2.0 认证流程。您的网络浏览器将打开，提示您登录并授权。
*   成功认证后，将在 `credentials/` 目录中创建一个 `token.json` 文件。此文件会安全地存储您的访问和刷新令牌，避免重复认证。

## 集成与配置

### 重要说明：本地 STDIO 服务

请注意，此 MCP 服务器是一个**本地服务**，它通过标准输入/输出 (STDIO) 与客户端进行通信。它**不是**一个需要部署在网络上的远程服务器，也**不会**监听任何网络端口。所有的工具调用都在您的本地计算机上执行，确保了数据的私密性和安全性。

### 方式一：集成到 Gemini CLI

您可以将此工具集成为 Gemini CLI 的一个插件。

1.  打开 Gemini CLI 的 `settings.json` 文件。您可以选择项目级或全局配置：
    *   **项目级**: 项目根目录下的 `.gemini/settings.json`。
    *   **全局**: 用户主目录下的 `~/.gemini/settings.json`。

2.  添加以下配置：

    ```json
    "google-office-tool": {
          "command": "uv",
          "args": [
            "run",
            "--with", "google-api-python-client",
            "--with", "google-auth-httplib2",
            "--with", "google-auth-oauthlib>=0.5.2",
            "--with", "fastmcp",
            "fastmcp",
            "run",
            "src/mcp-server/server.py"
          ],
          "cwd": "<YOUR_PROJECT_ROOT_DIRECTORY>"
        }
    ```

3.  **注意**: 如果您选择全局配置，请务必将 `<YOUR_PROJECT_ROOT_DIRECTORY>` 替换为此项目的**绝对路径**。对于项目级配置，则通常不需要 `cwd` 字段。

### 方式二：集成到 Cursor

您也可以将此 MCP 服务器集成到 Cursor 中，以便在 Cursor 的 AI 聊天中使用。

1.  **创建配置文件**:
    在您的用户主目录下的 `.cursor` 文件夹中，创建一个名为 `mcp.json` 的文件。
    *   **macOS / Linux**: `~/.cursor/mcp.json`
    *   **Windows**: `C:\Users\<YourUsername>\.cursor\mcp.json`

2.  **添加配置内容**:
    将以下 JSON 内容复制并粘贴到 `mcp.json` 文件中。

    **重要提示**: 请确保将 JSON 中的 `<YOUR_PROJECT_ROOT_DIRECTORY>` 替换为您本地存放此项目的**绝对路径**。

    ```json
    {
      "mcpServers": {
        "google-office-tool": {
          "command": "uv",
          "args": [
            "run",
            "--with", "fastapi==0.116.1",
            "--with", "google-api-python-client==2.177.0",
            "--with", "google-auth==2.40.3",
            "--with", "google-auth-httplib2==0.2.0",
            "--with", "google-auth-oauthlib==1.2.2",
            "--with", "pydantic==2.11.7",
            "--with", "pydantic_core==2.33.2",
            "--with", "uvicorn==0.35.0",
            "--with", "uvicorn-worker==0.3.0",
            "--with", "fastmcp==2.12.3",
            "fastmcp",
            "run",
            "<YOUR_PROJECT_ROOT_DIRECTORY>/src/mcp-server/server.py"
          ]
        }
      }
    }
    ```

3.  **重启 Cursor**:
    保存文件后，重启 Cursor。

## 如何使用

完成上述任一方式的配置和认证后，您就可以在相应的客户端（Gemini CLI 或 Cursor）中通过 `@google-office-tool` 来调用此项目提供的所有工具了。

### 支持的工具列表

| 工具名称 | 功能描述 |
| :--- | :--- |
| `create_google_doc_from_markdown` | 创建新的 Google 文档并将 Markdown 内容写入。 |
| `overwrite_google_doc` | **(新)** 重新写入现有文档。会自动清空文档内容并写入新的 Markdown。 |
| `append_content_to_google_doc` | 在现有 Google 文档的末尾追加 Markdown 内容。 |
| `replace_placeholders_in_google_doc` | 在文档中查找特定占位符（如 `{{key}}`）并替换为 Markdown 内容。 |
| `clear_google_doc_content` | 清空指定 Google 文档的正文内容。 |
| `read_google_doc_content` | 读取指定 Google 文档并将其内容输出为纯文本（含表格数据）。 |
| `create_google_slides_presentation` | 从符合特定协议的 Markdown 文件创建 Google Slides 演示文稿。 |
