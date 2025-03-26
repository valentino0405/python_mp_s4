#voice_commands.py
import speech_recognition as sr
import pyttsx3
import webbrowser
import threading
import cv2
from PIL import Image, ImageTk
import time
import os
import pygame
from fuzzywuzzy import process
from utils import (
    change_volume,
    play_specific_song,
    stop_music,
    list_songs,
    start_screen_recording,
    stop_screen_recording,
    capture_camera
)

# Video Path
VIDEO_PATH = "nanimation.mp4"

# Music Path (please replace with your actual music directory)
MUSIC_DIRECTORY = "music"

# Initialize TTS Engine
engine = pyttsx3.init()

# Initialize Pygame Mixer
pygame.mixer.init()

# Global flags
is_listening = False
is_music_playing = False
screen_recording_active = False
screen_recording_thread = None
screen_recording_filename = None

# Commands Dictionary
commands = {
    # Existing web commands
    "open youtube": "https://www.youtube.com",
    "open google": "https://www.google.com",
    "open github": "https://www.github.com",
    "open netflix": "https://www.netflix.com",

    # Music commands
    "open music": MUSIC_DIRECTORY,
    "open music folder": MUSIC_DIRECTORY,
    "stop music": "stop",

    # Screen recording commands
    "start recording": "start recording",
    "stop recording": "stop recording",

    # New volume and camera commands
    "set volume": "set volume",
    "open camera": "open camera",
    "capture image": "capture image",

    # SFIT pages
    "open homepage": "https://sfiterp.sfit.co.in:98/studentPortal.asp",
    "open sfit homepage": "https://sfiterp.sfit.co.in:98/studentPortal.asp",
    "open attendance": "https://sfiterp.sfit.co.in:98/StudPortal_Attendance.asp",
    "open grace attendance": "https://sfiterp.sfit.co.in:98/studportal_apply_grace_attendance.asp",
    "open iat result": "https://sfiterp.sfit.co.in:98/StudPortal_ExaminationReport.asp",
    "open final exam result": "https://sfiterp.sfit.co.in:98/StudPortal_EXAM_MArks.asp#",
    "open honors and minors result": "https://sfiterp.sfit.co.in:98/StudPortal_Honours_EXAM_MArks.asp",
    "open mcqs practice": "https://sfiterp.sfit.co.in:98/Studportal_Online_Quiz_Practice.asp",
    "open online quiz": "https://sfiterp.sfit.co.in:98/studportal_Online_Quiz.asp",
    "open online poll": "https://sfiterp.sfit.co.in:98/studportal_Online_poll.asp",
    "open session plan": "https://sfiterp.sfit.co.in:98/Studportal_Session_Plan.asp",
    "open sfit fees": "https://sfiterp.sfit.co.in:98/studportal_annual_fees.asp",
    "open academic bank of credits": "https://sfiterp.sfit.co.in:98/Studportal_ABCID.asp",
    "open upload photo": "https://sfiterp.sfit.co.in:98/studportal_capture_photo.asp",
    "open elections": "https://sfiterp.sfit.co.in:98/studportal_election.asp",

    # YouTube pages
    "open youtube shorts": "https://www.youtube.com/shorts",
    "open youtube subscriptions": "https://www.youtube.com/feed/subscriptions",
    "open youtube history": "https://www.youtube.com/feed/history",
    "open youtube playlist": "https://www.youtube.com/feed/playlists",
    "open youtube watch later": "https://www.youtube.com/playlist?list=WL",
    "open youtube liked videos": "https://www.youtube.com/playlist?list=LL",
    "open youtube downloads": "https://www.youtube.com/feed/downloads",
}

# Speak Function
def speak(text, status_label=None):
    if status_label:
        status_label.config(text=text)
    engine.say(text)
    engine.runAndWait()


# Play Video Animation with preserved aspect ratio
def play_video(is_listening, is_music_playing, video_label, video_frame):
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get original video dimensions
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_aspect_ratio = original_width / original_height

    while (is_listening or is_music_playing) and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            # Loop back to the beginning when the video ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Process and display the frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get current video display dimensions
        video_width = video_frame.winfo_width()
        video_height = video_frame.winfo_height()

        # Calculate the display size while preserving aspect ratio
        display_height = int(video_height * 0.8)
        display_width = int(display_height * original_aspect_ratio)

        # If calculated width exceeds available width, recalculate based on width
        if display_width > video_width * 0.8:
            display_width = int(video_width * 0.8)
            display_height = int(display_width / original_aspect_ratio)

        # Resize frame while preserving aspect ratio
        frame = cv2.resize(frame, (display_width, display_height))

        # Create a black image with the size of the video frame
        black_img = Image.new('RGB', (video_width, video_height), color='black')

        # Paste the video frame in the center
        x_offset = (video_width - display_width) // 2
        y_offset = (video_height - display_height) // 2

        frame_img = Image.fromarray(frame)
        black_img.paste(frame_img, (x_offset, y_offset))

        # Convert to PhotoImage
        imgtk = ImageTk.PhotoImage(image=black_img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        time.sleep(1 / fps)

    # Clear the video when not listening or music stopped
    video_label.configure(image="")
    cap.release()


# Process Commands
def process_command(command, status_label=None, video_label=None, video_frame=None):
    global is_music_playing, screen_recording_active
    command = command.lower()

    # Dependency injection for speak function
    def local_speak(text):
        speak(text, status_label)

    # Screen recording commands
    if command == "start recording":
        start_screen_recording(local_speak)
        return

    if command == "stop recording":
        stop_screen_recording(local_speak)
        return

    # Special handling for music-specific commands
    if command.startswith("play "):
        song_name = command.replace("play ", "")
        play_specific_song(song_name, MUSIC_DIRECTORY, local_speak)
        return

    # List songs command
    if command == "list songs":
        list_songs(MUSIC_DIRECTORY, local_speak)
        return

    # Volume Control Command
    if command.startswith("set volume"):
        try:
            # Extract volume level
            volume_level = int(command.split()[-1])
            change_volume(volume_level, local_speak)
        except (ValueError, IndexError):
            local_speak("Please specify a volume level between 0 and 100")
        return

    # Camera Commands
    if command in ["open camera", "capture image"]:
        capture_camera(local_speak, video_label, video_frame)
        return

    # Rest of the existing command processing logic
    best_match, score = process.extractOne(command, commands.keys())
    if score > 80:  # Adjust threshold if needed
        if best_match in ["open music", "open music folder"]:
            local_speak(f"Opening Music Folder")
            try:
                os.startfile(os.path.abspath(MUSIC_DIRECTORY))
            except Exception as e:
                local_speak(f"Error opening music folder: {str(e)}")
        elif best_match == "stop music":
            stop_music(local_speak)
        else:
            site_name = best_match.replace("open ", "").capitalize()
            local_speak(f"Opening {site_name}")
            webbrowser.open(commands[best_match])
    else:
        local_speak("Command not recognized. Please try again.")


# Listen for Voice Command
def listen(status_label=None, video_label=None, video_frame=None):
    global is_listening
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if status_label:
            status_label.config(text="Listening...")

        is_listening = True

        # Start video animation
        if video_label and video_frame:
            threading.Thread(target=play_video, args=(is_listening, is_music_playing, video_label, video_frame),
                             daemon=True).start()

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()

            if status_label:
                status_label.config(text=f"You said: {command}")

            process_command(command, status_label, video_label, video_frame)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.", status_label)
        except sr.RequestError:
            speak("There was an issue with the recognition service.", status_label)
        except Exception as e:
            speak(f"An error occurred: {str(e)}", status_label)

        is_listening = False


# Start Assistant
def start_voice_assistant(status_label=None, video_label=None, video_frame=None):
    if not is_listening:
        threading.Thread(target=listen, args=(status_label, video_label, video_frame), daemon=True).start()