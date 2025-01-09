# handy

A powerful voice-controlled productivity tool that combines speech recognition with AI assistance and keyboard automation. This tool allows users to control their computer, generate code, and interact with AI using voice commands triggered by keyboard shortcuts.

## Features

- 🎙️ Local transcription using MLX Whisper
- 🤖 AI-powered command execution and responses using OpenRouter (Claude)
- 💻 Code generation through voice commands
- ⌨️ Keyboard shortcut automation
- 📝 Direct text input from voice
- 📋 Smart context awareness using clipboard

## Keyboard Shortcuts

- CTRL + SHIFT (Left): Execute voice commands for keyboard shortcuts
- CTRL + CMD (Right): Transcribe voice to text
- SHIFT + ALT (Left): Get AI assistance with context awareness
- CTRL + ALT + CMD (Left): Generate code from voice input with context support

## Requirements

```python
openai
pynput
sounddevice
mlx_whisper
pydantic
pyperclip
numpy
python-dotenv
```

## Environment Variables

The following environment variables need to be set:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key
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
   - Hold `CTRL + ALT + CMD` (Left)
   - Say "create a Python function to sort a list"
   - Release keys to get the generated code

2. **AI Assistance**:
   - Hold `SHIFT + ALT` (Left)
   - Select text for context (optional)
   - Ask your question
   - Release to get AI response

3. **Voice Transcription**:
   - Hold `CTRL + CMD` (Right)
   - Speak your text
   - Release to transcribe

4. **Keyboard Commands**:
   - Hold `CTRL + SHIFT` (Left)
   - Say "copy" or "paste" or other keyboard shortcuts
   - Release to execute the command

## Architecture

- `AudioRecorder`: Handles real-time audio recording and processing
- `KeyboardShortcut`: Manages keyboard combinations and actions
- `ContextManager`: Handles clipboard-based context awareness
- AI Integration: Uses OpenRouter with Claude for intelligent responses
- MLX Whisper: Provides fast and accurate speech-to-text conversion

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- MLX Whisper for speech recognition
- OpenRouter and Claude for AI capabilities
- The open-source community for various dependencies