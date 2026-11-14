# Mistral API examples: OCR, STT, TTS

Working examples for Mistral's document and audio APIs using the V2 Python SDK.

## Setup

```bash
pip install -r requirements.txt
```

Provide your key from [Studio → API keys](https://console.mistral.ai/api-keys) in **one** of these ways — never paste it into chat or commit it:

```bash
export MISTRAL_API_KEY="your-api-key"        # shell env var
```

or create a `.env` file next to the scripts (already gitignored):

```bash
echo 'MISTRAL_API_KEY=your-api-key' > .env  # one line, in this directory only
```

The scripts check the environment first, then fall back to `.env`.

### On a phone

- **GitHub Codespaces**: open the repo on github.com → Code → Create codespace, add `MISTRAL_API_KEY` as a Codespaces secret (repo Settings → Secrets → Codespaces), then run the scripts in the terminal — the key never enters chat or the repo.
- **Google Colab**: clone the repo in a notebook, store the key under Colab's Secrets (left sidebar key icon) and read it with `from google.colab import userdata; userdata.get("MISTRAL_API_KEY")`.
- **Termux (Android) / local clone**: clone the repo and create the `.env` file above with a text editor.
- **No code at all**: try the endpoints in the API playground in [Studio](https://console.mistral.ai) while logged in.

## OCR — extract markdown from a PDF or image

```bash
python ocr_example.py path/to/document.pdf -o output.md
python ocr_example.py https://arxiv.org/pdf/2201.04234
```

Uses `mistral-ocr-latest` via `client.ocr.process`. Local files are sent as base64 data URLs.

## STT — transcribe an audio file

```bash
python stt_example.py recording.mp3
```

Uses `voxtral-mini-transcribe-3` via `client.audio.transcriptions.complete` and prints the transcript.
For live streaming transcription use `voxtral-mini-transcribe-realtime-3` (see the Mistral docs).

## TTS — synthesize speech

```bash
python tts_example.py "Hi there! You are listening to Voxtral." -o hello.wav
```

Uses `voxtral-mini-tts-3-0` via `client.audio.speech.complete` with the preset voice `gb_jane_neutral` and saves a WAV.

## Models referenced

| Task | Model | API |
| --- | --- | --- |
| OCR | `mistral-ocr-latest` | `client.ocr.process` (`/v1/ocr`) |
| STT (batch) | `voxtral-mini-transcribe-3` | `client.audio.transcriptions.complete` (`/v1/audio/transcriptions`) |
| STT (realtime) | `voxtral-mini-transcribe-realtime-3` | websocket `/v1/audio/transcriptions/realtime` |
| TTS | `voxtral-mini-tts-3-0` | `client.audio.speech.complete` (`/v1/audio/speech`) |

Docs: [OCR](https://docs.mistral.ai/studio/document-processing/basic_ocr), [Speech-to-text](https://docs.mistral.ai/studio/audio/speech-to-text/overview), [Text-to-speech](https://docs.mistral.ai/studio/audio/text-to-speech/generate-speech).
