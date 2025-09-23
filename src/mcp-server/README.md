# Google Office Tool MCP 服务器

本文件提供有关如何设置和使用 Google Office Tool MCP 服务器的说明。该服务器允许您通过 Gemini CLI 与 Google Docs 和 Google Slides API 进行交互。

## 先决条件

在您使用此工具之前，您需要设置您的 Google Cloud 项目并创建 OAuth 2.0 凭据。

1.  **Google Cloud 项目**:
    *   确保您有一个 Google Cloud 项目。
    *   为您的项目启用 **Google Docs API** 和 **Google Slides API**。

2.  **OAuth 2.0 凭据**:
    *   为“桌面应用程序”创建 OAuth 2.0 凭据。
    *   将凭据下载为 JSON 文件。
    *   将下载的文件重命名为 `oauth-credentials.json`。

## 设置

1.  **放置凭据文件**:
    *   将 `oauth-credentials.json` 文件放置在 `credentials/` 目录中。

2.  **配置 Gemini CLI**:
    *   您需要将以下配置添加到您的 Gemini CLI `settings.json` 文件中。您可以选择在项目级别或全局安装。

    *   **项目级安装**:
        *   将配置添加到项目根目录下的 `.gemini/settings.json` 文件中。

    *   **全局安装**:
        *   手动将配置添加到主目录下的 `~/.gemini/settings.json` 文件中。

    **配置:**
    ```json
    "google-office-tool": {
          "command": "uv",
          "args": [
            "run",
            "--with",
            "google-api-python-client",
            "--with",
            "google-auth-httplib2",
            "--with",
            "google-auth-oauthlib>=0.5.2",
            "--with",
            "fastmcp",
            "fastmcp",
            "run",
            "src/mcp-server/server.py"
          ],
          "cwd": "<YOUR_PROJECT_ROOT_DIRECTORY>"
        }
    ```

    **注意:** 如果您在全局 `settings.json` 中配置此工具，建议使用 `cwd` 字段来指定项目的绝对路径。请将 `<YOUR_PROJECT_ROOT_DIRECTORY>` 替换为您电脑上存放此项目的文件夹的绝对路径。如果是在项目级的 `.gemini/settings.json` 中配置，则通常不需要 `cwd` 字段，因为命令会默认在项目根目录执行。

## 认证

*   首次运行时，该工具将启动 OAuth 2.0 流程。您的网络浏览器将打开，系统将提示您授权该应用程序。
*   成功认证后，将在 `credentials/` 目录中创建一个 `token.json` 文件。此文件存储您的访问和刷新令牌，因此您不必每次都重新进行身份验证。

## 如何使用

完成设置和身份验证后，您可以通过 Gemini CLI 使用 `google-office-tool` 与您的 Google Docs 和 Slides 进行交互。