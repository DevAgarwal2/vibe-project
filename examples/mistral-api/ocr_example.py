import argparse
import base64
import mimetypes
import os

from mistralai.client import Mistral


def encode_local_file(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode('utf-8')}"


def main():
    parser = argparse.ArgumentParser(description="OCR a PDF or image with mistral-ocr-latest")
    parser.add_argument("source", help="Path to a local PDF/image or a public URL")
    parser.add_argument("-o", "--output", help="Write extracted markdown to this file instead of stdout")
    args = parser.parse_args()

    if args.source.startswith(("http://", "https://")):
        document = {"type": "document_url", "document_url": args.source}
    else:
        data_url = encode_local_file(args.source)
        if data_url.startswith("data:image/"):
            document = {"type": "image_url", "image_url": data_url}
        else:
            document = {"type": "document_url", "document_url": data_url}

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document=document,
        table_format="html",
    )

    markdown = "\n\n".join(page.markdown for page in response.pages)
    if args.output:
        with open(args.output, "w") as f:
            f.write(markdown)
        print(f"wrote {len(response.pages)} page(s) to {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
