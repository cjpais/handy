import os
import time
import mlx_whisper
from pynput import keyboard
import sounddevice as sd
import numpy as np
import threading
import queue
import pyautogui
import wave

from functions import process_transcription

# pyautogui.PAUSE = 0.01


class AudioRecorder:
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.keyboard_controller = keyboard.Controller()
        
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
            self._process_audio(audio_data)

    def _process_audio(self, audio_data):
        print("Processing audio...")
        
        # Generate timestamp for unique filename
        wav_filename = "tmp.wav"
        
        # Save audio data to WAV file
        with wave.open(wav_filename, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        print(f"Audio saved to {wav_filename}")

        # Time the transcription
        transcribe_start = time.time()
        transcription = mlx_whisper.transcribe(
            wav_filename,  # Now using the WAV file path
            path_or_hf_repo="mlx-community/whisper-small-mlx"
        )["text"].strip()
        transcribe_time = time.time() - transcribe_start
        print(f"Transcription took {transcribe_time:.2f} seconds: {transcription}")

        os.remove(wav_filename)

        # Time the processing
        process_start = time.time()
        process_transcription(transcription)
        process_time = time.time() - process_start
        print(f"Processing took {process_time:.2f} seconds")

def main():
    recorder = AudioRecorder()
    
    def on_press(key):
        if key == keyboard.Key.alt:  # Option key for normal typing
            recorder.start_recording()


    def on_release(key):
        if key == keyboard.Key.alt:  # Option key on Mac
            recorder.stop_recording()
            
    # Set up keyboard listener
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
