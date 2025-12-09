import argparse
import os
from auth import get_services_with_oauth, get_services_with_service_account
from google_docs import append_to_google_doc, clear_google_doc, write_to_google_doc, replace_markdown_placeholders, read_google_doc
from google_slider import create_presentation_from_markdown

def main():
    parser = argparse.ArgumentParser(description="Google Office Tool CLI")
    parser.add_argument("--auth_method", choices=["oauth", "service_account"], default="oauth", help="Authentication method")
    parser.add_argument("--creds_path", default="credentials/oauth-credentials.json", help="Path to credentials file")
    parser.add_argument("--token_path", default="credentials/token.json", help="Path to token file")
    parser.add_argument("--sa_path", default="credentials/docs-writer-credentials.json", help="Path to service account file")

    subparsers = parser.add_subparsers(dest="tool")

    # Google Docs Tool
    docs_parser = subparsers.add_parser("docs")
    docs_subparsers = docs_parser.add_subparsers(dest="command")

    write_parser = docs_subparsers.add_parser("write")
    write_parser.add_argument("markdown_file")
    write_parser.add_argument("--doc_id")
    write_parser.add_argument("--title", default="Untitled Document")
    write_parser.add_argument("--folder_id")
    write_parser.add_argument("--header_image", help="Path to local image file to add as header")
    write_parser.add_argument("--no-header", action="store_true", help="Do not add a header image")

    append_parser = docs_subparsers.add_parser("append")
    append_parser.add_argument("doc_id")
    append_parser.add_argument("text", nargs="?")
    append_parser.add_argument("--file", help="Path to a markdown file to append")

    clear_parser = docs_subparsers.add_parser("clear")
    clear_parser.add_argument("doc_id")

    replace_parser = docs_subparsers.add_parser("replace")
    replace_parser.add_argument("doc_id")
    replace_parser.add_argument("placeholder")
    replace_parser.add_argument("markdown_or_text")

    read_parser = docs_subparsers.add_parser("read")
    read_parser.add_argument("doc_id")

    # Google Slides Tool
    slides_parser = subparsers.add_parser("slides")
    slides_subparsers = slides_parser.add_subparsers(dest="command")

    create_parser = slides_subparsers.add_parser("create")
    create_parser.add_argument("markdown_file")
    create_parser.add_argument("--folder_id")
    create_parser.add_argument("--template_id")
    create_parser.add_argument("--title")

    args = parser.parse_args()

    if args.auth_method == "oauth":
        services = get_services_with_oauth(args.creds_path, args.token_path)
    else:
        services = get_services_with_service_account(args.sa_path)

    if args.tool == "docs":
        if args.command == "write":
            with open(args.markdown_file, "r") as f:
                content = f.read()
            
            header_image_path = None
            if args.no_header:
                header_image_path = None
            elif args.header_image:
                header_image_path = args.header_image
            else:
                # Default path
                base_dir = os.path.dirname(os.path.abspath(__file__))
                default_logo = os.path.join(base_dir, "assets", "default_header_logo.png")
                if os.path.exists(default_logo):
                    header_image_path = default_logo
            
            result = write_to_google_doc(services["docs"], services["drive"], content, args.title, args.doc_id, args.folder_id, header_image_path)
            if result["status"] == "success":
                print(f"Successfully created and wrote to document: https://docs.google.com/document/d/{result['document_id']}")
                print(f"Document ID: {result['document_id']}")
            else:
                print(f"An error occurred: {result['message']}")
        elif args.command == "append":
            content = ""
            content_source = ""
            if args.file:
                with open(args.file, "r") as f:
                    content = f.read()
                content_source = f"from {args.file}"
            elif args.text:
                content = args.text
                content_source = "text"

            if content:
                result = append_to_google_doc(services["docs"], args.doc_id, content)
                if result.get("status") == "success":
                    print(f"Appended content {content_source} to document {args.doc_id}")
                else:
                    print(f"An error occurred: {result.get('message', 'Unknown error')}")
        elif args.command == "clear":
            clear_google_doc(services["docs"], args.doc_id)
            print(f"Document {args.doc_id} cleared")
        elif args.command == "replace":
            content = ""
            if os.path.isfile(args.markdown_or_text):
                with open(args.markdown_or_text, "r") as f:
                    content = f.read()
            else:
                content = args.markdown_or_text
            replacements = {args.placeholder: content}
            result = replace_markdown_placeholders(services["docs"], args.doc_id, replacements)
            if result.get("status") == "success":
                print(f"Replaced placeholder '{args.placeholder}' in document {args.doc_id}")
            else:
                print(f"An error occurred: {result.get('message', 'Unknown error')}")
        elif args.command == "read":
            result = read_google_doc(services["docs"], args.doc_id)
            if result["status"] == "success":
                print(result["content"])
            else:
                print(f"An error occurred: {result['message']}")

    elif args.tool == "slides":
        if args.command == "create":
            create_presentation_from_markdown(services, args.markdown_file, args.folder_id, args.template_id, args.title)
            print(f"Presentation created from {args.markdown_file}")

if __name__ == "__main__":
    main()