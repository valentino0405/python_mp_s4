# utils.py
import os
import cv2
import time
import pygame
import threading
import pyautogui
import numpy as np
from PIL import Image, ImageTk
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import difflib

def change_volume(volume_level, speak_func):
    """
    Change system volume on Windows with precise control
    """
    try:
        # Get default audio device
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        # Ensure volume is within 0-100 range
        volume_level = max(0, min(volume_level, 100))

        # Set volume directly using SetMasterVolumeLevelScalar
        volume.SetMasterVolumeLevelScalar(volume_level / 100.0, None)
        speak_func(f"Volume set to {volume_level}%")

    except Exception as e:
        speak_func(f"Error changing volume: {str(e)}")

def play_specific_song(song_name, music_directory, speak_func):
    try:
        # Get list of music files in the directory
        music_files = [f for f in os.listdir(music_directory) if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]

        # Find the best matching song
        def find_best_match(song_name, file_list):
            # Remove file extensions for matching
            file_names_without_ext = [os.path.splitext(f)[0].lower() for f in file_list]

            # Use difflib to find the best match
            matches = difflib.get_close_matches(song_name.lower(), file_names_without_ext, n=1, cutoff=0.6)

            if matches:
                # Find the full filename that matches the best match
                matched_filename = [f for f in file_list if matches[0].lower() in f.lower()][0]
                return matched_filename
            return None

        # Find the best matching song
        matched_song = find_best_match(song_name, music_files)

        if matched_song:
            # Full path to the music file
            music_path = os.path.join(music_directory, matched_song)

            # Load and play the music
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()

            speak_func(f"Playing {matched_song}")
        else:
            speak_func(f"Could not find a song matching '{song_name}'")

    except Exception as e:
        speak_func(f"Error playing music: {str(e)}")

def stop_music(speak_func):
    try:
        pygame.mixer.music.stop()
        speak_func("Music stopped")
    except Exception as e:
        speak_func(f"Error stopping music: {str(e)}")

def list_songs(music_directory, speak_func):
    try:
        music_files = [f for f in os.listdir(music_directory) if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]
        if music_files:
            song_list = ", ".join([os.path.splitext(song)[0] for song in music_files])
            speak_func(f"Available songs: {song_list}")
        else:
            speak_func("No music files found in the music directory")
    except Exception as e:
        speak_func(f"Error listing songs: {str(e)}")

def start_screen_recording(speak_func):
    try:
        # Create Videos directory if it doesn't exist
        os.makedirs("Videos", exist_ok=True)
        # Generate unique filename with timestamp
        screen_recording_filename = f"Videos/screen_recording_{int(time.time())}.mp4"
        # Screen dimensions
        screen_size = pyautogui.size()
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(screen_recording_filename, fourcc, 20.0,
                              (screen_size.width, screen_size.height))

        def record_screen():
            nonlocal out
            while True:
                # Capture screen
                screenshot = pyautogui.screenshot()
                frame = np.array(screenshot)

                # Convert RGB to BGR (OpenCV requirement)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Write the frame
                out.write(frame)

                # Control frame rate (20 FPS)
                time.sleep(1 / 20)

        # Start recording in a separate thread
        screen_recording_thread = threading.Thread(target=record_screen)
        screen_recording_thread.start()

        speak_func("Screen recording started")
        return screen_recording_filename

    except Exception as e:
        speak_func(f"Error starting screen recording: {str(e)}")
        return None

def stop_screen_recording(speak_func):
    try:
        # Stop recording threads
        for thread in threading.enumerate():
            if thread.name == 'screen_recording_thread':
                thread.join()

        speak_func("Screen recording stopped")
    except Exception as e:
        speak_func(f"Error stopping screen recording: {str(e)}")

def capture_camera(speak_func, video_label=None, video_frame=None):
    try:
        # Create directory to save pictures if it doesn't exist
        if not os.path.exists('captured_images'):
            os.makedirs('captured_images')

        # Open the default camera
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            speak_func("Error: Could not open camera.")
            return

        # Capture a single frame
        ret, frame = cap.read()
        cap.release()

        if not ret:
            speak_func("Failed to capture image")
            return

        # Generate unique filename
        picture_count = len(os.listdir('captured_images')) + 1
        filename = f'captured_images/picture_{picture_count}.jpg'

        # Save the image
        cv2.imwrite(filename, frame)
        speak_func(f"Image captured and saved as {filename}")

        # Display the captured image in the video frame if components are provided
        if video_label and video_frame:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            captured_image = Image.fromarray(frame_rgb)

            # Resize image to fit video frame while maintaining aspect ratio
            video_width = video_frame.winfo_width()
            video_height = video_frame.winfo_height()
            captured_image.thumbnail((video_width, video_height), Image.LANCZOS)

            imgtk = ImageTk.PhotoImage(image=captured_image)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

    except Exception as e:
        speak_func(f"Error in camera capture: {str(e)}")