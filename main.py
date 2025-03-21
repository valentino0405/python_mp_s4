import tkinter as tk
import speech_recognition as sr
import pyttsx3
import webbrowser
import threading
import cv2
from PIL import Image, ImageTk
import time
from fuzzywuzzy import process

# Video Path - Make sure this path is correct
VIDEO_PATH = "nanimation.mp4"

# Initialize TTS Engine
engine = pyttsx3.init()

# Global flag
is_listening = False

# Commands Dictionary (kept the same as your original)
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


# Play Video Animation
def play_video():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        status_label.config(text="Error: Could not open video file")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    # Use the entire video instead of specific frames
    while is_listening and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            # Loop back to the beginning when the video ends
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Process and display the frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize while maintaining aspect ratio
        h, w = frame.shape[:2]
        video_width = video_frame.winfo_width()
        video_height = video_frame.winfo_height()

        # Calculate scaling factor
        scale = min(video_width / w, video_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        frame = cv2.resize(frame, (new_w, new_h))

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        root.update_idletasks()
        time.sleep(1 / fps)

    # Clear the video when not listening
    video_label.configure(image="")
    cap.release()


# Start Assistant
def start_voice_assistant():
    if not is_listening:
        threading.Thread(target=listen, daemon=True).start()


# UI Setup
root = tk.Tk()
root.title("AI Assistant")
root.geometry("800x600")
root.configure(bg="#000000")
root.minsize(600, 500)

# Make window content responsive
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Main frame
main_frame = tk.Frame(root, bg="#000000")
main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
main_frame.grid_rowconfigure(0, weight=3)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Video frame
video_frame = tk.Frame(main_frame, bg="#000000")
video_frame.grid(row=0, column=0, sticky="nsew")
video_frame.grid_rowconfigure(0, weight=1)
video_frame.grid_columnconfigure(0, weight=1)

# Video label (to display the video)
video_label = tk.Label(video_frame, bg="#000000")
video_label.grid(row=0, column=0, sticky="nsew")

# Slogan label
slogan_label = tk.Label(
    main_frame,
    text="A NEW ERA OF INTELLIGENCE BEGINS NOW.",
    font=("Consolas", 16, "bold"),
    fg="#FFFFFF",
    bg="#000000"
)
slogan_label.grid(row=1, column=0, sticky="ew", pady=10)

# Status label
status_label = tk.Label(
    main_frame,
    text="Waiting for command...",
    font=("Consolas", 12),
    fg="#00FFFF",
    bg="#000000"
)
status_label.grid(row=2, column=0, sticky="ew", pady=5)

# Listen Button in a separate frame for better positioning
button_frame = tk.Frame(main_frame, bg="#000000")
button_frame.grid(row=3, column=0, sticky="ew", pady=20)
button_frame.grid_columnconfigure(0, weight=1)


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
    relief="flat",
    padx=20,
    pady=10,
    activebackground="#00FFFF",
    activeforeground="#000000"
)
listen_button.grid(row=0, column=0)
listen_button.bind("<Enter>", on_enter)
listen_button.bind("<Leave>", on_leave)

# Start GUI
root.mainloop()