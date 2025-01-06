from enum import Enum
import os
from typing import List
import openai
from pydantic import BaseModel
from pynput.keyboard import Key, Controller
import time

import pyperclip

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

claude = openai.OpenAI(
    base_url="https://api.anthropic.com/v1",
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

keyboard = Controller()

def write_to_text_field(text: str):
    original_clipboard = pyperclip.paste()
    pyperclip.copy(text)

    time.sleep(0.05)
    execute_keyboard_shortcut(KeyboardShortcut(modifiers=[ModifierKey.COMMAND], letter_key='v'))
    time.sleep(0.05)

    pyperclip.copy(original_clipboard)

def instruct(transcription: str):
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant. You will receive voice transcriptions from a user that may include both a command/question and some minimal context to help you respond appropriately.

For example, the user might say:
- A direct question with no context: "What is the capital of France?"
- A command with context: "get commit message I fixed the bug in the login system"

Treat any context provided after the initial command/question as relevant information to help formulate your response. Keep responses concise and focused on addressing the user's specific need."""
        },
        {"role": "user", "content": transcription}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )

    message = response.choices[0].message
    # keyboard.type(message.content)
    write_to_text_field(message.content)

def code(transcription: str):
    messages = [
        {
            "role": "system",
            "content": """You are a code-only assistant. Output ONLY the exact code requested by the user, with no markdown formatting, no explanations, and no additional text. The code should be ready to copy and paste directly into an editor. Never use backticks.

If the user provides context or requirements after their initial request, use that information to generate the appropriate code. Do not include any commentary or descriptions - just the raw code implementation."""
        },
        {"role": "user", "content": transcription}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )

    message = response.choices[0].message
    # keyboard.type(message.content)
    write_to_text_field(message.content)

class ModifierKey(str, Enum):
    COMMAND = "command"
    CTRL = "ctrl"
    SHIFT = "shift"
    ALT = "alt"
    OPTION = "option"
    WINDOWS = "windows"
    BACKSPACE = "backspace"
    TAB = "tab"
    ENTER = "enter"
    ESCAPE = "escape"

class KeyboardShortcut(BaseModel):
    modifiers: List[ModifierKey]
    letter_key: str

class TypeTranscription(BaseModel):
    text: str

def execute_keyboard_shortcut(shortcut: KeyboardShortcut):
    """Execute keyboard shortcuts with multiple modifier keys"""
    key_mapping = {
        ModifierKey.COMMAND: Key.cmd,
        ModifierKey.CTRL: Key.ctrl,
        ModifierKey.SHIFT: Key.shift,
        ModifierKey.ALT: Key.alt,
        ModifierKey.OPTION: Key.alt,
        ModifierKey.WINDOWS: Key.cmd,
        ModifierKey.BACKSPACE: Key.backspace,
        ModifierKey.TAB: Key.tab,
        ModifierKey.ENTER: Key.enter,
        ModifierKey.ESCAPE: Key.esc,
    }

    print(f"executing keyboard shortcut: {shortcut}")
    
    try:
        # Convert modifier strings to actual keys
        modifier_keys = [key_mapping[mod] for mod in shortcut.modifiers]
        
        # Press all modifier keys
        for mod_key in modifier_keys:
            keyboard.press(mod_key)
        
        # Press and release the letter key
        keyboard.press(shortcut.letter_key.lower())
        time.sleep(0.1)

        keyboard.release(shortcut.letter_key.lower())
        
        # Release all modifier keys in reverse order
        for mod_key in reversed(modifier_keys):
            keyboard.release(mod_key)
            
        print(f"Executed keyboard shortcut: {'+'.join(mod.value for mod in shortcut.modifiers)}+{shortcut.letter_key}")
        
    except Exception as e:
        print(f"Error executing keyboard shortcut: {e}")
        # Release all keys in case of error
        for mod_key in modifier_keys:
            keyboard.release(mod_key)

def type_transcription(transcription: TypeTranscription):
    """Type and display the transcription text"""
    print(f"Typed transcription: {transcription.text}")
    write_to_text_field(transcription.text)

# Define the tools using Pydantic models
tools = [
    openai.pydantic_function_tool(KeyboardShortcut, name="execute_keyboard_shortcut", description="Execute keyboard shortcuts with multiple modifier keys"),
]

def command(transcription: str):
    """Process the transcription using OpenAI's API"""
    messages = [
        {
            "role": "system",
            "content": """You are an assistant that is given a keyboard shortcut to execute."""
        },
        {"role": "user", "content": transcription}
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Use appropriate model
            messages=messages,
            tools=tools
        )

        # Handle the response
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            
            if tool_call.function.name == "execute_keyboard_shortcut":
                shortcut = KeyboardShortcut.model_validate_json(tool_call.function.arguments)
                execute_keyboard_shortcut(shortcut)
            else:
                print(f"Unknown tool: {tool_call.function.name}")
                print(f"response: {response}")

    except Exception as e:
        print(f"Error processing transcription: {e}")
