# Mistral API examples: OCR, STT, TTS

Working examples for Mistral's document and audio APIs using the V2 Python SDK.

## Setup

```bash
pip install -r requirements.txt
export MISTRAL_API_KEY="your-api-key"   # get one at https://console.mistral.ai/api-keys
```

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
