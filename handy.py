import os
import time
from functions import code, command, instruct, write_to_text_field
import mlx_whisper
from pynput import keyboard
import sounddevice as sd
import numpy as np
import queue
import wave
from typing import Callable, Set, Dict, Union
from dataclasses import dataclass

@dataclass
class ShortcutConfig:
    keys: Set[keyboard.Key]
    callback: Callable[[str], None]
    active: bool = False
    pressed_keys: Set[keyboard.Key] = None

    def __post_init__(self):
        self.pressed_keys = set()

class AudioRecorder:
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.keyboard_controller = keyboard.Controller()
        self.shortcuts: Dict[str, ShortcutConfig] = {}
        
        # Pre-initialize audio device
        sd.default.samplerate = self.sample_rate
        sd.default.channels = self.channels
        
        # Start continuous recording
        self.stream = sd.InputStream(
            callback=self._audio_callback,
            samplerate=self.sample_rate,
            channels=self.channels
        )
        self.stream.start()

    def add_shortcut(self, shortcut_id: str, keys: Set[Union[keyboard.Key, str]], callback: Callable[[str], None]):
        """Add a new keyboard shortcut configuration"""
        self.shortcuts[shortcut_id] = ShortcutConfig(keys=set(keys), callback=callback)

    def _audio_callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_queue.put(indata.copy())

    def start_recording(self):
        print("Starting recording...")
        self.recording = True
        self.audio_data = []

    def stop_recording(self):
        print("Stopping recording...")
        self.recording = False
        
        # Collect all audio data from queue
        while not self.audio_queue.empty():
            self.audio_data.append(self.audio_queue.get())

        if self.audio_data:
            # Combine all audio chunks
            audio_data = np.concatenate(self.audio_data)
            return self._process_audio(audio_data)

    def _process_audio(self, audio_data):
        print("Processing audio...")
        
        wav_filename = "tmp.wav"
        
        # Save audio data to WAV file
        with wave.open(wav_filename, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        print(f"Audio saved to {wav_filename}")

        # Time the transcription
        transcribe_start = time.time()
        transcription = mlx_whisper.transcribe(
            wav_filename,
            path_or_hf_repo="mlx-community/whisper-small-mlx"
        )["text"].strip()
        transcribe_time = time.time() - transcribe_start
        print(f"Transcription took {transcribe_time:.2f} seconds: {transcription}")

        os.remove(wav_filename)
        return transcription

    def handle_key_event(self, key, is_press: bool):
        for shortcut_id, config in self.shortcuts.items():
            if is_press:
                try:
                    # Handle both Key objects and character keys
                    actual_key = key if isinstance(key, keyboard.Key) else key.char
                    if actual_key in config.keys:
                        config.pressed_keys.add(actual_key)
                        if config.pressed_keys == config.keys and not config.active:
                            config.active = True
                            self.start_recording()
                except AttributeError:
                    pass
            else:
                try:
                    actual_key = key if isinstance(key, keyboard.Key) else key.char
                    if actual_key in config.pressed_keys:
                        config.pressed_keys.remove(actual_key)
                        if config.active:
                            config.active = False
                            transcription = self.stop_recording()
                            if transcription and config.callback:
                                config.callback(transcription)
                except AttributeError:
                    pass

    def start_listening(self):
        with keyboard.Listener(
            on_press=lambda key: self.handle_key_event(key, True),
            on_release=lambda key: self.handle_key_event(key, False)
        ) as listener:
            listener.join()

def main():
    recorder = AudioRecorder()

    # ctrl_l + shift_l
    recorder.add_shortcut(
        "command",
        {keyboard.Key.ctrl_l, keyboard.Key.shift_l},
        command 
    )

    # ctrl_l + alt_l

    # ctrl_l + cmd_l

    # ctrl_r + cmd_r
    recorder.add_shortcut(
        "transcribe",
        {keyboard.Key.ctrl_r, keyboard.Key.cmd_r},
        write_to_text_field
    )

    # shift_l + alt_l
    recorder.add_shortcut(
        "instruct",
        {keyboard.Key.shift_l, keyboard.Key.alt_l},
        instruct
    )

    recorder.add_shortcut(
        "code",
        {keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.cmd_l},
        code
    )
    
    recorder.start_listening()

if __name__ == "__main__":
    main()
