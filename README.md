# handy

A powerful voice-controlled productivity tool that combines speech recognition with AI assistance and keyboard automation. This tool allows users to control their computer, generate code, and interact with AI using voice commands triggered by keyboard shortcuts.

## Features

- 🎙️ Local transcription using MLX Whisper
- 🤖 AI-powered command execution and responses using Groq/Anthropic
- 💻 Code generation through voice commands
- ⌨️ Keyboard shortcut automation
- 📝 Direct text input from voice

## Keyboard Shortcuts

- CTRL + SHIFT (Left): Press and hold to execute voice commands. Release to stop recording, transcribe, and execute the command.
- CTRL + CMD (Right): Press and hold to transcribe voice to text. Release to stop recording and display the transcription.
- SHIFT + ALT (Left): Press and hold to get AI assistance. Release to stop recording, transcribe, and provide AI-generated responses.
- CMD + SHIFT (Left): Press and hold to generate code from voice input. Release to stop recording, transcribe, and generate code based on the voice input.

## Requirements

```python
openai
pynput
sounddevice
mlx_whisper
pydantic
pyperclip
numpy
```

## Environment Variables

The following environment variables need to be set:

```bash
GROQ_API_KEY=your_groq_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Set up environment variables as described above.

## Usage

1. Run the main script:
```bash
uv run handy.py
```

2. Use keyboard shortcuts to activate different modes:
   - Hold the designated key combination
   - Speak your command
   - Release the keys to process the command

## Examples

1. **Code Generation**:
   - Hold `CMD + SHIFT` (Left)
   - Say "create a Python function to sort a list"
   - Release keys to get the generated code

2. **AI Assistance**:
   - Hold `SHIFT + ALT` (Left)
   - Ask your question
   - Release to get AI response

3. **Voice Transcription**:
   - Hold `CTRL + CMD` (Right)
   - Speak your text
   - Release to transcribe

## Architecture

- `AudioRecorder`: Handles real-time audio recording and processing
- `KeyboardShortcut`: Manages keyboard combinations and actions
- AI Integration: Uses Groq and Anthropic for different types of responses
- MLX Whisper: Provides fast and accurate speech-to-text conversion

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- MLX Whisper for speech recognition
- Groq and Anthropic for AI capabilities
- The open-source community for various dependencies