from enum import Enum
import os
from typing import List
import anthropic
import openai
from pydantic import BaseModel
from pynput.keyboard import Key, Controller
import time

import pyperclip

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

openrouter = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

claude = anthropic.Anthropic()

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

def code(transcription: str, model="claude"):
    original_clipboard = pyperclip.paste()
    
    keyboard.press(Key.cmd)
    keyboard.press('c')
    keyboard.release('c')
    keyboard.release(Key.cmd)
    
    time.sleep(0.1)
    selected_text = pyperclip.paste()
    
    context = f"Selected text:\n{selected_text}\n\nRequest: {transcription}"

    sys_prompt = """You are a code-only assistant. I will provide you with selected text or clipboard content along with instructions. If I request code, output only the exact code implementation. If I request a terminal command, provide only the valid command syntax. Never use markdown, explanations, or additional text.

    When I share selected text or clipboard content, use that as context for generating your response. The output should be ready to copy and paste directly, with no formatting or commentary. For terminal commands, ensure they are valid for the specified environment. Note for terminal commands, I typically use lowercase instead of uppercase. You may also be given them directly, but need to translate them into a way that can actually be executed in the terminal because the transcription you are given might be poor.

    Output only:
    - Raw code implementation when code is requested
    - Terminal command syntax when a command is requested
    - No markdown, no backticks, no explanations
    - No additional text or descriptions"""
    
    messages = [{"role": "user", "content": context}]

    if model == "claude":
        response = claude.messages.create(
            model="claude-3-5-sonnet-latest",
            messages=messages,
            max_tokens=2048,
            system=sys_prompt
        )
        message = response.content[0].text
    elif model == "llama":
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        message = response.choices[0].message.content
    else:
        raise ValueError("Invalid model specified. Use 'claude' or 'llama'")

    write_to_text_field(message)
    pyperclip.copy(original_clipboard)

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

tools = [
    openai.pydantic_function_tool(KeyboardShortcut, name="execute_keyboard_shortcut", description="Execute keyboard shortcuts with multiple modifier keys"),
]

def command(transcription: str):
    messages = [
        {
            "role": "system",
            "content": "You are a keyboard shortcut assistant. Convert spoken commands into keyboard shortcuts and execute them using the execute_keyboard_shortcut tool. Only respond with valid keyboard shortcuts that can be executed."
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
                print(shortcut) 
                execute_keyboard_shortcut(shortcut)
            else:
                print(f"Unknown tool: {tool_call.function.name}")
                print(f"response: {response}")

    except Exception as e:
        print(f"Error processing transcription: {e}")
