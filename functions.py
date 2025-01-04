from enum import Enum
import os
from typing import List
import openai
from pydantic import BaseModel
from pynput.keyboard import Key, Controller
import time

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

keyboard = Controller()

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
    keyboard.type(transcription.text)

# Define the tools using Pydantic models
tools = [
    openai.pydantic_function_tool(KeyboardShortcut, name="execute_keyboard_shortcut", description="Execute keyboard shortcuts with multiple modifier keys"),
    openai.pydantic_function_tool(TypeTranscription, name="type_transcription", description="Type and display the transcription text")
]

def process_transcription(transcription: str):
    """Process the transcription using OpenAI's API"""
    messages = [
        {
            "role": "system",
            "content": """You are an assistant that processes voice transcriptions for computer navigation. You are assisting a person with one hand, it is CRITICAL that you follow the instructions:

1. For keyboard shortcuts (e.g., 'command P', 'ctrl shift S'): Call execute_keyboard_shortcut function with the appropriate modifier keys and letter key. Note that 'tab', 'enter', and 'backspace' are also valid modifier keys.
2. For all other text: Clean up transcription error. Your ONLY job is to clean up clear speech-to-text errors while preserving the exact message, then call type_transcription. 

Never respond directly to questions or provide explanations. Always call one of the available functions. You will be given only the transcription."""
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
            elif tool_call.function.name == "type_transcription":
                transcription = TypeTranscription.model_validate_json(tool_call.function.arguments)
                type_transcription(transcription)

    except Exception as e:
        print(f"Error processing transcription: {e}")
