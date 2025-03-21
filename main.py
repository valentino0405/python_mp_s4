import tkinter as tk
import speech_recognition as sr
import pyttsx3
import webbrowser
import threading
import cv2
from PIL import Image, ImageTk
import time
from fuzzywuzzy import process

# Video Path
VIDEO_PATH = "nanimation.mp4"

# Initialize TTS Engine
engine = pyttsx3.init()

# Global flag
is_listening = False

# Commands Dictionary
commands = {
    "open youtube": "https://www.youtube.com",
    "open google": "https://www.google.com",
    "open github": "https://www.github.com",
    "open netflix": "https://www.netflix.com",
    "open youtube history": "https://www.youtube.com/feed/history",

    # sfit pages
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

    # youtube pages
    "open youtube shorts": "https://www.youtube.com/shorts",
    "open youtube subscriptions": "https://www.youtube.com/feed/subscriptions",
    "open youtube history": "https://www.youtube.com/feed/history",
    "open youtube playlist": "https://www.youtube.com/feed/playlists",
    "open youtube watch later": "https://www.youtube.com/playlist?list=WL",
    "open youtube liked videos": "https://www.youtube.com/playlist?list=LL",
    "open youtube downloads": "https://www.youtube.com/feed/downloads",
}


# Speak Function
def speak(text):
    status_label.config(text=text)
    root.update_idletasks()
    engine.say(text)
    engine.runAndWait()


# Process Commands
def process_command(command):
    command = command.lower()
    best_match, score = process.extractOne(command, commands.keys())
    if score > 80:  # Adjust threshold if needed
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
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        status_label.config(text="Error: Could not open video file")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get original video dimensions
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_aspect_ratio = original_width / original_height

    while is_listening and cap.isOpened():
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

    # Clear the video when not listening
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