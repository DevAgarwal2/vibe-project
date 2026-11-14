import argparse
import os

from mistralai.client import Mistral

from mistral_env import load_env


def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file with Voxtral")
    parser.add_argument("audio", help="Path to an audio file (wav, mp3, ...)")
    parser.add_argument("--model", default="voxtral-mini-transcribe-3")
    args = parser.parse_args()
    load_env()

    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    with open(args.audio, "rb") as f:
        transcription = client.audio.transcriptions.complete(
            model=args.model,
            file={"file_name": os.path.basename(args.audio), "content": f},
        )
    print(transcription.text)


if __name__ == "__main__":
    main()
