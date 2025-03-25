import tkinter as tk
import speech_recognition as sr
import pyttsx3
import webbrowser
import threading
import cv2
from PIL import Image, ImageTk
import time
from fuzzywuzzy import process
import os
import pygame
import difflib
import pyautogui
import numpy as np

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


# Screen Recording Functions
def start_screen_recording():
    global screen_recording_active, screen_recording_thread, screen_recording_filename
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
        # Set global flag
        screen_recording_active = True

        def record_screen():
            nonlocal out
            while screen_recording_active:
                # Capture screen
                screenshot = pyautogui.screenshot()
                frame = np.array(screenshot)

                # Convert RGB to BGR (OpenCV requirement)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Write the frame
                out.write(frame)

                # Control frame rate (20 FPS)
                time.sleep(1 / 20)

            # Release the video writer when recording stops
            out.release()

        # Start recording in a separate thread
        screen_recording_thread = threading.Thread(target=record_screen)
        screen_recording_thread.start()

        speak("Screen recording started")
        return screen_recording_filename

    except Exception as e:
        speak(f"Error starting screen recording: {str(e)}")
        return None


def stop_screen_recording():
    global screen_recording_active, screen_recording_thread, screen_recording_filename

    if not screen_recording_active:
        speak("No active screen recording to stop")
        return

    # Stop the recording
    screen_recording_active = False

    # Wait for the recording thread to finish
    if screen_recording_thread:
        screen_recording_thread.join()

    speak(f"Screen recording stopped. Saved to {screen_recording_filename}")
    return screen_recording_filename


# Speak Function
def speak(text):
    status_label.config(text=text)
    root.update_idletasks()
    engine.say(text)
    engine.runAndWait()


# Music Player Functions
def play_specific_song(song_name):
    global is_music_playing
    try:
        # Get list of music files in the directory
        music_files = [f for f in os.listdir(MUSIC_DIRECTORY) if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]

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
            music_path = os.path.join(MUSIC_DIRECTORY, matched_song)

            # Load and play the music
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
            is_music_playing = True

            speak(f"Playing {matched_song}")
        else:
            speak(f"Could not find a song matching '{song_name}'")

    except Exception as e:
        speak(f"Error playing music: {str(e)}")


def stop_music():
    global is_music_playing
    try:
        pygame.mixer.music.stop()
        is_music_playing = False
        speak("Music stopped")
    except Exception as e:
        speak(f"Error stopping music: {str(e)}")


def list_songs():
    try:
        music_files = [f for f in os.listdir(MUSIC_DIRECTORY) if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]
        if music_files:
            song_list = ", ".join([os.path.splitext(song)[0] for song in music_files])
            speak(f"Available songs: {song_list}")
        else:
            speak("No music files found in the music directory")
    except Exception as e:
        speak(f"Error listing songs: {str(e)}")


# Process Commands
def process_command(command):
    global is_music_playing, screen_recording_active
    command = command.lower()

    # Screen recording commands
    if command == "start recording":
        start_screen_recording()
        return

    if command == "stop recording":
        stop_screen_recording()
        return

    # Special handling for music-specific commands
    if command.startswith("play "):
        song_name = command.replace("play ", "")
        play_specific_song(song_name)
        return

    # List songs command
    if command == "list songs":
        list_songs()
        return

    # Rest of your existing command processing logic
    best_match, score = process.extractOne(command, commands.keys())
    if score > 80:  # Adjust threshold if needed
        if best_match in ["open music", "open music folder"]:
            speak(f"Opening Music Folder")
            try:
                os.startfile(os.path.abspath(MUSIC_DIRECTORY))
            except Exception as e:
                speak(f"Error opening music folder: {str(e)}")
        elif best_match == "stop music":
            stop_music()
        else:
            site_name = best_match.replace("open ", "").capitalize()
            speak(f"Opening {site_name}")
            webbrowser.open(commands[best_match])
    else:
        speak("Command not recognized. Please try again.")


# Listen for Voice Command
def listen():
    global is_listening
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="Listening...")
        root.update_idletasks()
        is_listening = True

        # Start video animation
        threading.Thread(target=play_video, daemon=True).start()

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            status_label.config(text=f"You said: {command}")
            process_command(command)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except sr.RequestError:
            speak("There was an issue with the recognition service.")
        except Exception as e:
            speak(f"An error occurred: {str(e)}")

        is_listening = False


# Play Video Animation with preserved aspect ratio
def play_video():
    global is_music_playing
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        status_label.config(text="Error: Could not open video file")
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

        root.update_idletasks()
        time.sleep(1 / fps)

    # Clear the video when not listening or music stopped
    video_label.configure(image="")
    cap.release()


# Exit fullscreen with Escape key
def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)
    root.geometry("800x600")


# Toggle fullscreen with F11 key
def toggle_fullscreen(event=None):
    is_fullscreen = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not is_fullscreen)


# Start Assistant
def start_voice_assistant():
    if not is_listening:
        threading.Thread(target=listen, daemon=True).start()


# UI Setup
root = tk.Tk()
root.title("AI Assistant")
root.configure(bg="#000000")

# Set to fullscreen
root.attributes("-fullscreen", True)

# Make window content responsive
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Add border frame
border_frame = tk.Frame(root, bg="#000000", bd=2, relief="solid", highlightbackground="#333333", highlightthickness=2)
border_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
border_frame.grid_rowconfigure(0, weight=1)
border_frame.grid_columnconfigure(0, weight=1)

# Main content frame inside the border
main_frame = tk.Frame(border_frame, bg="#000000")
main_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
main_frame.grid_rowconfigure(0, weight=4)  # Video area
main_frame.grid_rowconfigure(1, weight=1)  # Text area
main_frame.grid_columnconfigure(0, weight=1)

# Video frame with border
video_outer_frame = tk.Frame(main_frame, bg="#000000", bd=1, relief="solid", highlightbackground="#333333",
                             highlightthickness=1)
video_outer_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
video_outer_frame.grid_rowconfigure(0, weight=1)
video_outer_frame.grid_columnconfigure(0, weight=1)

# Video frame
video_frame = tk.Frame(video_outer_frame, bg="#000000")
video_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
video_frame.grid_rowconfigure(0, weight=1)
video_frame.grid_columnconfigure(0, weight=1)

# Video label (to display the video)
video_label = tk.Label(video_frame, bg="#000000")
video_label.grid(row=0, column=0, sticky="nsew")

# Text frame with border
text_outer_frame = tk.Frame(main_frame, bg="#000000", bd=1, relief="solid", highlightbackground="#333333",
                            highlightthickness=1)
text_outer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
text_outer_frame.grid_rowconfigure(0, weight=1)
text_outer_frame.grid_columnconfigure(0, weight=1)

# Text frame
text_frame = tk.Frame(text_outer_frame, bg="#000000")
text_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
text_frame.grid_rowconfigure(0, weight=1)
text_frame.grid_rowconfigure(1, weight=1)
text_frame.grid_rowconfigure(2, weight=1)
text_frame.grid_columnconfigure(0, weight=1)

# Slogan label
slogan_label = tk.Label(
    text_frame,
    text="A NEW ERA OF INTELLIGENCE BEGINS NOW.",
    font=("Consolas", 18, "bold"),
    fg="#FFFFFF",
    bg="#000000"
)
slogan_label.grid(row=0, column=0, sticky="s", pady=5)

# Status label
status_label = tk.Label(
    text_frame,
    text="Waiting for command...",
    font=("Consolas", 14),
    fg="#00FFFF",
    bg="#000000"
)
status_label.grid(row=1, column=0, sticky="n", pady=5)

# Listen Button
button_frame = tk.Frame(text_frame, bg="#000000")
button_frame.grid(row=2, column=0, sticky="n", pady=10)


# Listen Button Style
def on_enter(e):
    listen_button.config(bg="#00FFFF", fg="#000000")


def on_leave(e):
    listen_button.config(bg="#000000", fg="#00FFFF")


listen_button = tk.Button(
    button_frame,
    text="ACTIVATE",
    command=start_voice_assistant,
    font=("Consolas", 14, "bold"),
    bg="#000000",
    fg="#00FFFF",
    borderwidth=1,
    relief="solid",
    padx=20,
    pady=10,
    activebackground="#00FFFF",
    activeforeground="#000000"
)
listen_button.pack()
listen_button.bind("<Enter>", on_enter)
listen_button.bind("<Leave>", on_leave)

# Keyboard bindings
root.bind("<Escape>", exit_fullscreen)
root.bind("<F11>", toggle_fullscreen)

# Start GUI
root.mainloop()