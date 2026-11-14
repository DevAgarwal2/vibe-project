import argparse
import base64
import os

from mistralai.client import Mistral

from mistral_env import load_env


def main():
    parser = argparse.ArgumentParser(description="Synthesize speech with Voxtral TTS")
    parser.add_argument("text", help="Text to speak")
    parser.add_argument("-o", "--output", default="output.wav", help="Output file (default: output.wav)")
    parser.add_argument("--model", default="voxtral-mini-tts-3-0")
    parser.add_argument("--voice", default="gb_jane_neutral", help="Preset voice_id")
    args = parser.parse_args()
    load_env()

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    response = client.audio.speech.complete(
        model=args.model,
        input=args.text,
        voice_id=args.voice,
        response_format="wav",
    )
    with open(args.output, "wb") as f:
        f.write(base64.b64decode(response.audio_data))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
